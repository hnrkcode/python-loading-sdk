import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Self

import httpx

from loading_sdk import _api, _http
from loading_sdk._api import Operation, T


async def async_loading_api_client(
    email: str | None = None,
    password: str | None = None,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    timeout: float = 300.0,
) -> "AsyncLoadingApiClient":
    """Create an async client and log in when both credentials are supplied."""
    client = AsyncLoadingApiClient(transport=transport, timeout=timeout)
    if email and password:
        try:
            login = await client._authenticate(email, password)
            if login.get("code") == 200:
                client._cookies = login.get("cookies")
        except BaseException:
            await client.aclose()
            raise
    return client


class AsyncLoadingApiClient:
    """Async Loading.se client. Use an async context manager to reuse connections."""

    def __init__(
        self,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 300.0,
    ) -> None:
        self._timeout = timeout
        self._transport = transport
        self._client = self._new_client() if transport is not None else None
        self._closed = False
        self._entered = False
        self._cookies: httpx.Cookies | None = None

    def _new_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=self._transport,
            timeout=httpx.Timeout(self._timeout, connect=min(30.0, self._timeout)),
            follow_redirects=True,
            event_hooks={
                "request": [_http.async_before_send],
                "response": [_http.async_after_receive],
            },
        )

    async def __aenter__(self) -> Self:
        if self._closed or self._entered:
            raise RuntimeError("SDK client is closed or already entered")
        if self._client is None:
            self._client = self._new_client()
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        """Close the SDK-owned connection pool and any supplied transport."""
        if not self._closed and self._client is not None:
            await self._client.aclose()
        self._closed = True

    @asynccontextmanager
    async def _session(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        if self._client is not None:
            yield self._client
        else:
            async with self._new_client() as client:
                yield client

    async def _run(self, operation: Operation[T]) -> T:
        if self._closed:
            raise RuntimeError("SDK client is closed")
        try:
            req = next(operation)
        except StopIteration as done:
            return done.value
        async with self._session() as client:
            while True:
                _http.prepare(req, self._cookies)
                try:
                    async with asyncio.timeout(self._timeout):
                        response = await client.send(req)
                except TimeoutError as exc:
                    raise httpx.TimeoutException(
                        "Request exceeded its total timeout", request=req
                    ) from exc
                try:
                    req = operation.send(response)
                except StopIteration as done:
                    return done.value

    async def _authenticate(self, email: str, password: str) -> dict[str, Any]:
        return await self._run(_api.authenticate(email, password))

    async def get_profile(self) -> dict[str, Any]:
        """Return the authenticated user's profile."""
        return await self._run(_api.get_profile())

    async def search(self, query: str) -> dict[str, Any]:
        """Return posts matching the search query."""
        return await self._run(_api.search(query))

    async def get_post(self, post_id: str) -> dict[str, Any]:
        """Return the post with the given ID."""
        return await self._run(_api.get_post(post_id))

    async def get_thread(
        self, thread_id: str, page: int | None = None
    ) -> dict[str, Any]:
        """Return one page of posts from the thread, starting at page 1."""
        return await self._run(_api.get_thread(thread_id, page))

    async def get_games(self, page: int | None = None) -> dict[str, Any]:
        """Return one page of threads from the games forum."""
        return await self._run(_api.category_page("games", page))

    async def get_other(self, page: int | None = None) -> dict[str, Any]:
        """Return one page of threads from the other forum."""
        return await self._run(_api.category_page("other", page))

    async def get_editorials(
        self,
        page: int | None = None,
        post_type: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """Return one page of editorials from the texts category.

        The default ``post_type`` is ``neRegular``. Other supported filters are
        ``review``, ``opinion``, ``update``, ``podcast``, and ``conversation``.
        Pass ``sort="title"`` to sort alphabetically. The default order is by date.
        """
        return await self._run(_api.category_page("texts", page, post_type, sort))

    async def create_post(self, thread_id: str, message: str) -> dict[str, Any]:
        """Post a Markdown reply to the thread."""
        return await self._run(_api.create_post(thread_id, message))

    async def edit_post(self, post_id: str, message: str) -> dict[str, Any]:
        """Replace a post's body with the supplied Markdown text."""
        return await self._run(_api.edit_post(post_id, message))

    async def create_thread(
        self, title: str, message: str, category_name: str, post_type: str | None = None
    ) -> dict[str, Any]:
        """Create a thread in the ``games`` or ``other`` forum.

        The message is the Markdown body. The default post type is ``regular``.
        """
        return await self._run(
            _api.create_thread(title, message, category_name, post_type)
        )

    async def edit_thread(self, thread_id: str, message: str) -> dict[str, Any]:
        """Replace the thread's opening message with the supplied Markdown text."""
        return await self._run(_api.edit_thread(thread_id, message))

    async def get_about(self) -> dict[str, Any]:
        """Return the site's editorial staff and moderators."""
        return await self._run(_api.get_about())

    async def get_socials(self) -> dict[str, Any]:
        """Return the site's social media links."""
        return await self._run(_api.get_socials())

    async def get_total_thread_pages(self, thread_id: str) -> int | dict[str, Any]:
        """Return the thread's page count or the error dictionary from ``get_thread()``."""
        return await self._run(_api.get_total_thread_pages(thread_id))

    async def get_total_category_pages(self, category: str) -> dict[str, Any]:
        """Count pages in the ``games``, ``other``, or ``texts`` category.

        On success, ``response["data"]["total_pages"]`` contains the count.
        """
        return await self._run(_api.get_total_category_pages(category))
