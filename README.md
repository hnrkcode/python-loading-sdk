# Python Loading SDK

[![PyPI Version][pypi-image]][pypi-url]
[![][versions-image]][versions-url]
[![Build Status][build-image]][build-url]

[pypi-image]: https://img.shields.io/pypi/v/python-loading-sdk
[pypi-url]: https://pypi.org/project/python-loading-sdk/
[versions-image]: https://img.shields.io/pypi/pyversions/python-loading-sdk
[versions-url]: https://pypi.org/project/python-loading-sdk/
[build-image]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml/badge.svg
[build-url]: https://github.com/hnrkcode/python-loading-sdk/actions/workflows/build.yaml

## Install

Requires Python 3.11 or newer.

```
pip install python-loading-sdk
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

## Usage

Instantiate the client and optionally provide login credentials to be able to use methods that requires the user to be logged in.

```python
from loading_sdk import LoadingApiClient

client = LoadingApiClient(email="your@email.com", password="your_password")

response = client.get_profile()
```

It can also be used asyncrounously:

```python
from loading_sdk import AsyncLoadingApiClient

client = await AsyncLoadingApiClient(email="your@email.com", password="your_password")

response = await client.get_profile()
```

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
