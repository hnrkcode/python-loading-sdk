from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Self

import httpx

from loading_sdk import _api, _http
from loading_sdk._api import Operation, T


class LoadingApiClient:
    """Synchronous Loading.se client. Use a context manager to reuse connections."""

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        *,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._timeout = timeout
        self._transport = transport
        self._client = self._new_client() if transport is not None else None
        self._closed = False
        self._entered = False
        self._cookies: httpx.Cookies | None = None
        if email and password:
            try:
                login = self._authenticate(email, password)
                if login.get("code") == 200:
                    self._cookies = login.get("cookies")
            except BaseException:
                self.close()
                raise

    def _new_client(self) -> httpx.Client:
        return httpx.Client(
            transport=self._transport,
            timeout=self._timeout,
            follow_redirects=True,
            event_hooks={
                "request": [_http.before_send],
                "response": [_http.after_receive],
            },
        )

    def __enter__(self) -> Self:
        if self._closed or self._entered:
            raise RuntimeError("SDK client is closed or already entered")
        if self._client is None:
            self._client = self._new_client()
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Close the SDK-owned connection pool and any supplied transport."""
        if not self._closed and self._client is not None:
            self._client.close()
        self._closed = True

    @contextmanager
    def _session(self) -> Generator[httpx.Client, None, None]:
        if self._client is not None:
            yield self._client
        else:
            with self._new_client() as client:
                yield client

    def _run(self, operation: Operation[T]) -> T:
        if self._closed:
            raise RuntimeError("SDK client is closed")
        try:
            req = next(operation)
        except StopIteration as done:
            return done.value
        with self._session() as client:
            while True:
                _http.prepare(req, self._cookies)
                response = client.send(req)
                try:
                    req = operation.send(response)
                except StopIteration as done:
                    return done.value

    def _authenticate(self, email: str, password: str) -> dict[str, Any]:
        return self._run(_api.authenticate(email, password))

    def get_profile(self) -> dict[str, Any]:
        """Return the authenticated user's profile."""
        return self._run(_api.get_profile())

    def search(self, query: str) -> dict[str, Any]:
        """Return posts matching the search query."""
        return self._run(_api.search(query))

    def get_post(self, post_id: str) -> dict[str, Any]:
        """Return the post with the given ID."""
        return self._run(_api.get_post(post_id))

    def get_thread(self, thread_id: str, page: int | None = None) -> dict[str, Any]:
        """Return one page of posts from the thread, starting at page 1."""
        return self._run(_api.get_thread(thread_id, page))

    def get_games(self, page: int | None = None) -> dict[str, Any]:
        """Return one page of threads from the games forum."""
        return self._run(_api.category_page("games", page))

    def get_other(self, page: int | None = None) -> dict[str, Any]:
        """Return one page of threads from the other forum."""
        return self._run(_api.category_page("other", page))

    def get_editorials(
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
        return self._run(_api.category_page("texts", page, post_type, sort))

    def create_post(self, thread_id: str, message: str) -> dict[str, Any]:
        """Post a Markdown reply to the thread."""
        return self._run(_api.create_post(thread_id, message))

    def edit_post(self, post_id: str, message: str) -> dict[str, Any]:
        """Replace a post's body with the supplied Markdown text."""
        return self._run(_api.edit_post(post_id, message))

    def create_thread(
        self, title: str, message: str, category_name: str, post_type: str | None = None
    ) -> dict[str, Any]:
        """Create a thread in the ``games`` or ``other`` forum.

        The message is the Markdown body. The default post type is ``regular``.
        """
        return self._run(_api.create_thread(title, message, category_name, post_type))

    def edit_thread(self, thread_id: str, message: str) -> dict[str, Any]:
        """Replace the thread's opening message with the supplied Markdown text."""
        return self._run(_api.edit_thread(thread_id, message))

    def get_about(self) -> dict[str, Any]:
        """Return the site's editorial staff and moderators."""
        return self._run(_api.get_about())

    def get_socials(self) -> dict[str, Any]:
        """Return the site's social media links."""
        return self._run(_api.get_socials())

    def get_total_thread_pages(self, thread_id: str) -> int | dict[str, Any]:
        """Return the thread's page count or the error dictionary from ``get_thread()``."""
        return self._run(_api.get_total_thread_pages(thread_id))

    def get_total_category_pages(self, category: str) -> dict[str, Any]:
        """Count pages in the ``games``, ``other``, or ``texts`` category.

        On success, ``response["data"]["total_pages"]`` contains the count.
        """
        return self._run(_api.get_total_category_pages(category))
