# Release notes

## 0.5.0 (2026-11-23)

Python 3.11 is the minimum supported version. The test suite covers Python 3.11 through 3.15. Projects on Python 3.8–3.10 can continue using 0.4.1.

- Both clients now use HTTPX. The public imports, synchronous constructor, awaitable async factory, and API response dictionaries are preserved. Callers that catch network exceptions should catch `httpx.RequestError`, or a subclass such as `httpx.ConnectError` or `httpx.TimeoutException`.
- Ordinary operations close their connections automatically. Use `with` or `async with` to reuse connections across operations. Supplying a custom transport transfers ownership to the SDK. Release it with the context manager, `close()`, or `await aclose()`.
- Sync requests default to 10 seconds per network phase. Async requests default to a 300-second total deadline per request, including redirects, with a 30-second connection timeout. Both factories accept a keyword-only `timeout` in seconds.
- Login cookies follow cookie domain, path, and security attributes and are sent only on authenticated calls to the API origin. A redirect that would replay an authenticated form to another origin raises `httpx.RequestError`.
- An empty category returns zero pages. `get_total_thread_pages()` returns an integer on success or an error dictionary on failure. `get_about()` reads the site's editorial endpoint and returns the existing `people` and `moderators` fields.
