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
        """Returns authenticated users profile data

        :rtype: dict
        """
        return self._run(_api.get_profile())

    def search(self, query: str) -> dict[str, Any]:
        """Returns posts that matches the query

        :param query: Search query
        :type query: str
        :rtype: dict
        """
        return self._run(_api.search(query))

    def get_post(self, post_id: str) -> dict[str, Any]:
        """Returns a specific post

        :param post_id: unique post id
        :type post_id: str
        :rtype: dict
        """
        return self._run(_api.get_post(post_id))

    def get_thread(self, thread_id: str, page: int | None = None) -> dict[str, Any]:
        """Returns all posts on a specific page from a specific thread

        :param thread_id: unique thread_id
        :type thread_id: str
        :param page: thread page (**optional**)
        :type page: int
        :rtype: dict
        """
        return self._run(_api.get_thread(thread_id, page))

    def get_games(self, page: int | None = None) -> dict[str, Any]:
        """Retruns threads from a specific page in the game category

        :param page: Game forum page
        :type page: int
        :rtype: dict
        """
        return self._run(_api.category_page("games", page))

    def get_other(self, page: int | None = None) -> dict[str, Any]:
        """Retruns threads from a specific page in the other category

        :param page: Other forum page
        :type page: int
        :rtype: dict
        """
        return self._run(_api.category_page("other", page))

    def get_editorials(
        self,
        page: int | None = None,
        post_type: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """Retruns threads from a specific page in the texts category

        :param page: Texts forum page (**optional**)
        :type page: int
        :param post_type: Articles can be of post_type: "review", "opinion", "update", "podcast",
            or "conversation" (**optional**)
        :type post_type: str
        :param sort: Sort the returned threads by date by the default, but if "title" is used as
            a parameter it's sorted by thread title instead. (**optional**)
        :type sort: str
        :rtype: dict
        """
        return self._run(_api.category_page("texts", page, post_type, sort))

    def create_post(self, thread_id: str, message: str) -> dict[str, Any]:
        """Create new post in a thread

        :param thread_id: Unique thread id
        :type thread_id: str
        :param message: Text that can be formatted with markdown that will be posted in the thread
        :type message: str
        :rtype: dict
        """
        return self._run(_api.create_post(thread_id, message))

    def edit_post(self, post_id: str, message: str) -> dict[str, Any]:
        """Edit existing post in a thread

        :param post_id: Unique post id
        :type post_id: str
        :param message: New text, that can be formatted with markdown,
            that will replace the old message
        :type message: str
        :rtype: dict
        """
        return self._run(_api.edit_post(post_id, message))

    def create_thread(
        self, title: str, message: str, category_name: str, post_type: str | None = None
    ) -> dict[str, Any]:
        """Create new thread in one of the forum categories

        :param title: Thread title
        :type title: str
        :param message: Thread body that can be formatted with markdown
        :type message: str
        :param category_name: Forum category. Can be either "games" or "other".
        :type category_name: str
        :param post_type: Creates a "regular" thread by the default. (**optional**)
        :rtype: dict
        """
        return self._run(_api.create_thread(title, message, category_name, post_type))

    def edit_thread(self, thread_id: str, message: str) -> dict[str, Any]:
        """Edit existing thread

        :param thread_id: Unique thread id
        :type thread_id: str
        :param message: New text, that can be formatted with markdown,
            that will replace the old message
        :type message: str
        :rtype: dict
        """
        return self._run(_api.edit_thread(thread_id, message))

    def get_about(self) -> dict[str, Any]:
        """Get about page data

        :rtype dict
        """
        return self._run(_api.get_about())

    def get_socials(self) -> dict[str, Any]:
        """Get social media links

        :rtype dict
        """
        return self._run(_api.get_socials())

    def get_total_thread_pages(self, thread_id: str) -> int | dict[str, Any]:
        """Returns total pages of a thread.

        :param thread_id: Unique thread id
        :type thread_id: str
        :returns: The page count, or the error dictionary returned by get_thread.
        :rtype: int | dict
        """
        return self._run(_api.get_total_thread_pages(thread_id))

    def get_total_category_pages(self, category: str) -> dict[str, Any]:
        """Returns total pages of a forum category.

        :param category: Category name. Can be games, other, or texts
        :type category: str
        :rtype: dict
        """
        return self._run(_api.get_total_category_pages(category))
