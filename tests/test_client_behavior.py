import inspect

import pytest

from loading_sdk import AsyncLoadingApiClient, LoadingApiClient
from loading_sdk.async_api import client as async_client
from loading_sdk.async_api import extractors as async_extractors
from loading_sdk.sync_api import client as sync_client
from loading_sdk.sync_api import extractors as sync_extractors

pytestmark = pytest.mark.asyncio


async def resolve(value):
    """Exercise the same public operation on either client."""
    return await value if inspect.isawaitable(value) else value


@pytest.fixture(params=[LoadingApiClient, AsyncLoadingApiClient], ids=["sync", "async"])
def make_client(request, monkeypatch, httpserver):
    base_url = httpserver.url_for("").rstrip("/")
    for module in (sync_client, async_client):
        monkeypatch.setattr(module, "API_URL", base_url)
    for module in (sync_extractors, async_extractors):
        monkeypatch.setattr(module, "BASE_URL", base_url)
    return request.param


@pytest.mark.parametrize("authenticated", [True, False], ids=["accepted", "rejected"])
async def test_login_then_profile(make_client, httpserver, authenticated):
    credentials = {"email": "reader@example.org", "password": "test"}
    login = httpserver.expect_ordered_request(
        "/v1/auth/login", method="POST", data_form=credentials
    )
    if authenticated:
        login.respond_with_json({}, headers={"Set-Cookie": "jwt=example; Path=/"})
        httpserver.expect_ordered_request(
            "/v1/users/profile", method="GET", headers={"Cookie": "jwt=example"}
        ).respond_with_json({"name": "reader"})
        expected = {"code": 200, "message": "OK", "data": {"name": "reader"}}
    else:
        login.respond_with_json({"code": 401}, status=401)
        expected = {"code": 401, "message": "No auth token"}
        httpserver.expect_ordered_request(
            "/v1/users/profile", method="GET"
        ).respond_with_json(expected, status=401)

    client = await resolve(make_client(**credentials))
    assert await resolve(client.get_profile()) == expected
    if not authenticated:
        assert "Cookie" not in httpserver.log[-1][0].headers


@pytest.mark.parametrize("pages", [0, 1, 5])
async def test_category_pages(make_client, httpserver, pages):
    # Each probe may be used just once, so a broken search cannot loop forever.
    for page in range(1, 9):
        httpserver.expect_oneshot_request(
            "/v1/posts/",
            method="GET",
            headers={"texts": "texts", "post-type": "neRegular", "page": str(page)},
        ).respond_with_json({"posts": [{"title": "thread"}] if page <= pages else []})

    client = await resolve(make_client())
    assert await resolve(client.get_total_category_pages("texts")) == {
        "code": 200,
        "message": "OK",
        "data": {"total_pages": pages},
    }


@pytest.mark.parametrize(("replies", "pages"), [(0, 1), (30, 1), (31, 2)])
async def test_thread_pages(make_client, httpserver, replies, pages):
    httpserver.expect_request("/v1/posts/thread").respond_with_json(
        {"posts": [{"title": "thread", "replies": replies}]}
    )
    client = await resolve(make_client())
    assert await resolve(client.get_total_thread_pages("thread")) == pages


async def test_thread_pages_missing_thread(make_client, httpserver):
    expected = {"code": 404, "message": "Thread does not exist"}
    httpserver.expect_request("/v1/posts/thread").respond_with_json(
        expected, status=404
    )
    client = await resolve(make_client())
    assert await resolve(client.get_total_thread_pages("thread")) == expected


async def test_thread_pages_for_reply(make_client, httpserver):
    httpserver.expect_request("/v1/posts/reply").respond_with_json({"posts": [{}]})
    client = await resolve(make_client())
    assert await resolve(client.get_total_thread_pages("reply")) == {
        "code": 200,
        "message": "Exists, but was not a thread id",
    }


async def test_about_extraction(make_client, httpserver):
    httpserver.expect_request("/om").respond_with_data(
        '<script src="/static/js/main.abc.js"></script>'
    )
    httpserver.expect_request("/static/js/main.abc.js").respond_with_data(
        'static/js/x{1:"def"}[id]+".chunk.js"'
    )
    httpserver.expect_request("/static/js/1.def.chunk.js").respond_with_data(
        'var e=[{name:"Editor"}].map(x),a=[{name:"Moderator"}].map(x)'
    )
    client = await resolve(make_client())
    assert await resolve(client.get_about()) == {
        "code": 200,
        "message": "OK",
        "data": {"people": [{"name": "Editor"}], "moderators": [{"name": "Moderator"}]},
    }


async def test_socials_extraction(make_client, httpserver):
    httpserver.expect_request("/").respond_with_data(
        '<script src="/static/js/main.abc.js"></script>'
    )
    httpserver.expect_request("/static/js/main.abc.js").respond_with_data(
        'href:"https://www.example.org/loading",target:"_blank",rel:"noreferrer noopener",className:"Footer-icon"'
    )
    client = await resolve(make_client())
    assert await resolve(client.get_socials()) == {
        "code": 200,
        "message": "OK",
        "data": [{"name": "example", "link": "https://www.example.org/loading"}],
    }


async def test_about_without_chunks(make_client, httpserver):
    httpserver.expect_request("/om").respond_with_data(
        '<script src="/static/js/main.abc.js"></script>'
    )
    httpserver.expect_request("/static/js/main.abc.js").respond_with_data("/* empty */")
    client = await resolve(make_client())
    assert await resolve(client.get_about()) == {
        "code": 404,
        "message": "No data found",
        "data": None,
    }


async def test_missing_main_script(make_client, httpserver):
    httpserver.expect_request("/").respond_with_data("<html></html>")
    client = await resolve(make_client())
    assert await resolve(client.get_socials()) == {
        "code": 404,
        "message": "No results found",
        "data": None,
    }
