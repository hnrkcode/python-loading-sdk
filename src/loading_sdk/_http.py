"""Cookie and redirect policy shared by the HTTPX clients."""

import httpx

from loading_sdk import settings


def api_origin(url: httpx.URL) -> bool:
    api = httpx.URL(settings.API_URL)
    return (url.scheme, url.host, url.port) == (api.scheme, api.host, api.port)


def prepare(request: httpx.Request, cookies: httpx.Cookies | None) -> None:
    if request.extensions.get("sdk_login"):
        request.extensions["sdk_cookies"] = httpx.Cookies()
    elif request.extensions.get("sdk_auth"):
        request.extensions["sdk_cookies"] = httpx.Cookies(cookies)


def before_send(request: httpx.Request) -> None:
    # HTTPX builds redirect requests from the pool's cookie jar. Apply the SDK's
    # per-operation jar on every hop, including redirects between sibling hosts.
    request.headers.pop("cookie", None)
    jar = request.extensions.get("sdk_cookies")
    if jar is None:
        return
    if api_origin(request.url):
        jar.set_cookie_header(request)
    elif request.method not in ("GET", "HEAD"):
        raise httpx.RequestError(
            "Refusing to forward an authenticated form to another origin",
            request=request,
        )


def after_receive(response: httpx.Response) -> None:
    jar = response.request.extensions.get("sdk_cookies")
    if jar is not None and api_origin(response.request.url):
        jar.extract_cookies(response)


async def async_before_send(request: httpx.Request) -> None:
    before_send(request)


async def async_after_receive(response: httpx.Response) -> None:
    after_receive(response)
