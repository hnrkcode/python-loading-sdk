import asyncio
import inspect
import json
from contextlib import AsyncExitStack
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

from loading_sdk import AsyncLoadingApiClient, LoadingApiClient

FIXTURES = Path(__file__).parent / "fixtures"
pytestmark = pytest.mark.asyncio


async def resolve(value):
    return await value if inspect.isawaitable(value) else value


@pytest.fixture(params=[LoadingApiClient, AsyncLoadingApiClient], ids=["sync", "async"])
def factory(request):
    return request.param


async def enter(stack, client):
    if isinstance(client, LoadingApiClient):
        return stack.enter_context(client)
    return await stack.enter_async_context(client)


async def test_site_fixtures(factory):
    editorial = json.loads((FIXTURES / "editorial.json").read_text(encoding="utf-8"))

    def handle(request):
        match (request.url.host, request.url.path):
            case ("api.loading.se", "/v1/editorial/"):
                return httpx.Response(200, json=editorial)
            case ("loading.se", "/"):
                return httpx.Response(
                    200, content=(FIXTURES / "loading.html").read_bytes()
                )
            case ("loading.se", "/static/js/main.314f4d19.js"):
                return httpx.Response(
                    200, content=(FIXTURES / "footer.js").read_bytes()
                )
            case _:
                pytest.fail(f"Unexpected request: {request.url}")

    async with AsyncExitStack() as stack:
        client = await enter(
            stack, await resolve(factory(transport=httpx.MockTransport(handle)))
        )
        assert await resolve(client.get_about()) == {
            "code": 200,
            "message": "OK",
            "data": {
                "people": editorial["editorials"],
                "moderators": editorial["moderators"],
            },
        }
        assert await resolve(client.get_socials()) == {
            "code": 200,
            "message": "OK",
            "data": [
                {"name": "twitter", "link": "https://twitter.com/loadingse"},
                {"name": "instagram", "link": "https://www.instagram.com/loading.se/"},
            ],
        }


async def test_form_and_cookie_scope_across_redirects(factory):
    message = "räksmörgås + a&b=c"

    def handle(request):
        match (request.url.host, request.url.path):
            case ("api.loading.se", "/v1/auth/login"):
                assert parse_qs(request.content.decode()) == {
                    "email": ["a+b@example.org"],
                    "password": [message],
                }
                return httpx.Response(
                    303,
                    headers=[
                        ("location", "/v1/login-complete"),
                        (
                            "set-cookie",
                            "jwt=test; Domain=.loading.se; Path=/v1; Secure",
                        ),
                        ("set-cookie", "limited=1; Path=/v1/users; Secure"),
                    ],
                )
            case ("api.loading.se", "/v1/login-complete"):
                assert (
                    request.method == "GET" and request.headers["cookie"] == "jwt=test"
                )
                return httpx.Response(200, json={})
            case ("api.loading.se", "/v1/users/profile"):
                assert set(request.headers["cookie"].split("; ")) == {
                    "limited=1",
                    "jwt=test",
                }
                return httpx.Response(
                    302, headers={"location": "https://loading.se/v1/redirected"}
                )
            case ("loading.se", "/v1/redirected"):
                assert "cookie" not in request.headers
                return httpx.Response(200, json={"name": "reader"})
            case ("api.loading.se", "/v1/posts/id"):
                if request.method == "GET":
                    assert "cookie" not in request.headers
                    return httpx.Response(200, json={})
                assert request.method == "POST"
                assert request.headers["cookie"] == "jwt=test"
                assert (
                    request.headers["content-type"]
                    == "application/x-www-form-urlencoded"
                )
                assert parse_qs(request.content.decode()) == {"body": [message]}
                return httpx.Response(201, json={"id": "1"})
            case _:
                pytest.fail(f"Unexpected request: {request.url}")

    async with AsyncExitStack() as stack:
        client = await enter(
            stack,
            await resolve(
                factory(
                    "a+b@example.org", message, transport=httpx.MockTransport(handle)
                )
            ),
        )
        assert await resolve(client.get_profile()) == {
            "code": 200,
            "message": "OK",
            "data": {"name": "reader"},
        }
        assert (await resolve(client.get_post("id")))["code"] == 200
        assert await resolve(client.create_post("id", message)) == {
            "code": 201,
            "message": "Post created",
            "data": {"id": "1"},
        }


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.ConnectError])
async def test_timeout_and_transport_error(factory, error):
    def handle(request):
        assert set(request.extensions["timeout"].values()) == {1.5}
        raise error("test transport", request=request)

    async with AsyncExitStack() as stack:
        client = await enter(
            stack,
            await resolve(factory(transport=httpx.MockTransport(handle), timeout=1.5)),
        )
        with pytest.raises(error) as caught:
            await resolve(client.get_profile())
        assert caught.value.request.url.path == "/v1/users/profile"


async def test_async_total_timeout():
    async def handle(request):
        await asyncio.sleep(5)
        pytest.fail("Total request deadline was not enforced")

    async with await AsyncLoadingApiClient(
        transport=httpx.MockTransport(handle), timeout=0.02
    ) as client:
        with pytest.raises(httpx.TimeoutException):
            await client.get_profile()


class TrackingTransport(httpx.MockTransport):
    closed = False

    def close(self):
        self.closed = True

    async def aclose(self):
        self.closed = True


async def test_failed_login_closes_owned_transport(factory):
    def redirect(request):
        assert request.url.host == "api.loading.se"
        return httpx.Response(307, headers={"location": "https://other.example/login"})

    transport = TrackingTransport(redirect)
    with pytest.raises(httpx.RequestError, match="another origin"):
        await resolve(factory("reader", "password", transport=transport))
    assert transport.closed


async def test_one_shot_and_context_ownership(factory, monkeypatch):
    pools = []
    client = await resolve(factory())
    http_type = (
        httpx.Client if isinstance(client, LoadingApiClient) else httpx.AsyncClient
    )

    def new_pool():
        pool = http_type(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
        )
        pools.append(pool)
        return pool

    monkeypatch.setattr(client, "_new_client", new_pool)

    assert (await resolve(client.get_profile()))["code"] == 200
    assert len(pools) == 1 and pools[0].is_closed
    async with AsyncExitStack() as stack:
        await enter(stack, client)
        for _ in range(2):
            assert (await resolve(client.get_profile()))["code"] == 200
        assert len(pools) == 2 and not pools[1].is_closed
    assert pools[1].is_closed
    with pytest.raises(RuntimeError, match="closed"):
        await resolve(client.get_profile())
