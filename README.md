# Python Loading SDK

[![PyPI Version][pypi-image]][pypi-url]
[![Supported Python versions][versions-image]][versions-url]
[![Build Status][build-image]][build-url]

[pypi-image]: https://img.shields.io/pypi/v/python-loading-sdk
[pypi-url]: https://pypi.org/project/python-loading-sdk/
[versions-image]: https://img.shields.io/pypi/pyversions/python-loading-sdk
[versions-url]: https://pypi.org/project/python-loading-sdk/
[build-image]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml/badge.svg
[build-url]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml

Access the Loading.se forums and editorial content from synchronous or asynchronous Python code.

## Install

Requires Python 3.11 or newer.

```
pip install python-loading-sdk
```

See the [release notes](https://github.com/hnrkcode/python-loading-sdk/blob/main/CHANGELOG.md) for Python support and HTTP behavior changes.

## Usage

Create a client without credentials to read public content. Provide credentials to access your profile or create and edit posts.

```python
from loading_sdk import LoadingApiClient

client = LoadingApiClient(email="your@email.com", password="your_password")

response = client.get_profile()
```

The async factory is awaitable.

```python
from loading_sdk import AsyncLoadingApiClient

client = await AsyncLoadingApiClient(email="your@email.com", password="your_password")

response = await client.get_profile()
```

### Connection ownership and errors

Ordinary calls open and close a temporary HTTPX client for each SDK operation. Pagination and extraction reuse that connection pool across their requests. Login cookies stay with the SDK instance between operations.

A context manager shares one pool across multiple operations.

```python
with LoadingApiClient() as client:
    games = client.get_games()
    socials = client.get_socials()

async with await AsyncLoadingApiClient() as client:
    games = await client.get_games()
    socials = await client.get_socials()
```

Both factories accept a keyword-only `transport` for custom HTTPX transports, including `httpx.MockTransport`. Supplying a transport gives the SDK ownership and enables pooling immediately. Use the context manager or call `close()` / `await aclose()` to release it. Each SDK instance needs its own transport.

The SDK follows redirects. It sends login cookies only on authenticated API calls, respecting the API origin and cookie domain, path, and security attributes. A redirect that would replay an authenticated form to another origin raises `httpx.RequestError`.

Sync requests default to a 10-second timeout per network phase. Async requests default to a 300-second total deadline per request, including redirects, with a 30-second connection timeout. Set `timeout` in seconds on either factory to change the deadline or phase limit. Network failures propagate as HTTPX exceptions, including `httpx.TimeoutException` and `httpx.ConnectError`. API error responses retain their SDK dictionary format.

## Examples

### Requires Auth

```python
response = client.get_profile()
```

```python
response = client.create_post(
    thread_id="5bbb986af1deda001d33bc4b", message="My message!"
)
```

```python
response = client.edit_post(
    post_id="5bc876dd70a79c001dab7ebe", message="My updated message!"
)
```

```python
response = client.create_thread(
    title="My title", message="The content!", category_name="games"
)
```

```python
response = client.edit_thread(
    thread_id="5bbb986af1deda001d33bc4b", message="My updated message!"
)
```

### Anonymous

```python
response = client.search(query="search query")
```

```python
response = client.get_post(post_id="5bc876dd70a79c001dab7ebe")
```

```python
response = client.get_thread(thread_id="5bbb986af1deda001d33bc4b", page=3)
```

```python
response = client.get_games(page=5)
```

```python
response = client.get_other(page=7)
```

```python
response = client.get_editorials(page=2, post_type="review", sort="title")
```

```python
response = client.get_about()
```

```python
response = client.get_socials()
```

```python
response = client.get_total_thread_pages(thread_id="5bbb986af1deda001d33bc4b")
```

```python
response = client.get_total_category_pages(category="games")
```

## Development

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run these commands from the checkout. The project defaults to Python 3.13.

```sh
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run pytest --cov=loading_sdk --cov-branch
uv build
```

The SDK lives in `src/loading_sdk/`. The build produces a wheel and source distribution in `dist/`. To build the documentation, run `uv run --locked --group docs sphinx-build -b html docs/source docs/build/html`.

### Publishing a release

Set the project version with `uv version`, commit the updated metadata and lockfile, and push a matching `v<version>` tag. A prerelease tag such as `v0.5.0rc1` targets TestPyPI. After its index verification succeeds, a stable tag such as `v0.5.0` targets PyPI.

Configure a GitHub Trusted Publisher on each index for `hnrkcode/python-loading-sdk`, workflow `pypi.yaml`, and the corresponding GitHub environment (`testpypi` or `pypi`). The workflow checks the distributions, uploads the verified files, and installs both downloads from the target index.
