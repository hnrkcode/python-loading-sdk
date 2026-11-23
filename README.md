# Python Loading SDK

[![PyPI Version][pypi-image]][pypi-url]
[![Supported Python versions][versions-image]][versions-url]
[![CI status on main][build-image]][build-url]

Read Loading.se forums and editorials, search posts, and join discussions from synchronous or asynchronous Python code.

## Installation

Requires Python 3.12 or later.

```sh
pip install python-loading-sdk
```

## Usage

### Read public threads

Use `LoadingApiClient` to read the games forum without credentials.

```python
from loading_sdk import LoadingApiClient

with LoadingApiClient() as client:
    response = client.get_games()
    if response["message"] == "OK":
        for thread in response["data"]["posts"]:
            print(thread["title"])
```

### Access your profile asynchronously

Both clients accept an email and password for profile access and posting. This example reads credentials from environment variables. With `AsyncLoadingApiClient`, await both client creation and each API call.

```python
import asyncio
import os

from loading_sdk import AsyncLoadingApiClient


async def main():
    async with await AsyncLoadingApiClient(
        email=os.environ["LOADING_EMAIL"],
        password=os.environ["LOADING_PASSWORD"],
    ) as client:
        response = await client.get_profile()
        if response["code"] == 200:
            print(response["data"]["name"])


asyncio.run(main())
```

## Operations

Use these calls with a synchronous client. With an async client, add `await` before each call.

### Public reads

```python
response = client.search(query="search query")
response = client.get_post(post_id="5bc876dd70a79c001dab7ebe")
response = client.get_thread(thread_id="5bbb986af1deda001d33bc4b", page=3)
response = client.get_games(page=5)
response = client.get_other(page=7)
response = client.get_editorials(page=2, post_type="review", sort="title")
response = client.get_about()
response = client.get_socials()
response = client.get_total_thread_pages(thread_id="5bbb986af1deda001d33bc4b")
response = client.get_total_category_pages(category="games")
```

### Requires login

```python
response = client.get_profile()

response = client.create_post(
    thread_id="5bbb986af1deda001d33bc4b", message="My message!"
)

response = client.edit_post(
    post_id="5bc876dd70a79c001dab7ebe", message="My updated message!"
)

response = client.create_thread(
    title="My title", message="The content!", category_name="games"
)

response = client.edit_thread(
    thread_id="5bbb986af1deda001d33bc4b", message="My updated message!"
)
```

## Connections and errors

- **Connection reuse.** Use `with` or `async with` to share a pool across operations. By default, each operation opens and closes its own pool. Login cookies persist on the SDK instance.
- **Custom transports.** Set `transport` to an HTTPX transport such as `httpx.MockTransport` to enable pooling immediately. Each client owns its transport. Release it with a context manager, `close()`, or `await aclose()`.
- **Timeouts.** Sync requests default to 10 seconds per network phase. Async requests have a 300-second total deadline including redirects, with a 30-second connection timeout. Set `timeout` in seconds to override the default.
- **Errors and redirects.** API errors return dictionaries. Network failures raise HTTPX exceptions. The SDK follows redirects and restricts login cookies to authenticated requests on the API origin. A redirect that would replay an authenticated form on another origin raises `httpx.RequestError`.

## Development

The checkout defaults to Python 3.15. From the repository root, install the locked dependencies with [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest --cov=loading_sdk --cov-branch
uv build
```

`uv build` writes the wheel and source distribution to `dist/`. For publishing instructions, see the [maintainer guide](https://github.com/hnrkcode/python-loading-sdk/blob/main/CONTRIBUTING.md#publishing-a-release).

### Documentation

Edit the user guide in `docs/source/index.rst` and the API descriptions in the client docstrings under `src/loading_sdk/`. Build the HTML preview with Sphinx.

```sh
uv run --locked --group docs sphinx-build -W -b html docs/source docs/build/html
```

Open `docs/build/html/index.html` in a browser. CI runs the same check, and Git ignores the generated HTML. PyPI displays this README as the project description.

[pypi-image]: https://img.shields.io/pypi/v/python-loading-sdk?cacheSeconds=300
[pypi-url]: https://pypi.org/project/python-loading-sdk/
[versions-image]: https://img.shields.io/pypi/pyversions/python-loading-sdk?cacheSeconds=300
[versions-url]: https://pypi.org/project/python-loading-sdk/
[build-image]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml/badge.svg?branch=main&event=push
[build-url]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml?query=branch%3Amain+event%3Apush
