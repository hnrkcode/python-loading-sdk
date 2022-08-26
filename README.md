# Python Loading SDK

## How to install

```
pip install python-loading-sdk
```

## Usage Examples

Instantiate the client and optionally provide login credentials to be able to use methods that requires the user to be logged in.

```python
from loading_sdk import LoadingApiClient

client = LoadingApiClient(email="your@email.com", password="your_password")
```

### Requires Auth

```python
response = client.get_profile()
```

```python
response = client.create_post(thread_id="5bbb986af1deda001d33bc4b", message="My message!")
```

```python
response = client.edit_post(post_id="5bc876dd70a79c001dab7ebe", message="My updated message!")
```

```python
response = client.create_thread(title="My title", message="The content!", category_name="games")
```

```python
response = client.edit_thread(post_id="5bbb986af1deda001d33bc4b", message="My updated message!")
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