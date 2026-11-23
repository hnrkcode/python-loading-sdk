Python Loading SDK
==================

Use version |release| of the SDK to read Loading.se forums and editorials
from Python. Install it with ``pip install python-loading-sdk`` on Python
3.12 or newer.

Read public content
-------------------

.. code-block:: python

   from loading_sdk import LoadingApiClient

   with LoadingApiClient() as client:
       response = client.get_post(post_id="5bb7aac18fef22001d90267b")
       if response["message"] == "OK":
           print(response["data"]["posts"][0]["body"])

Use an async client
-------------------

Await the factory to create a client. Pass your email and password to either
client to access your profile or write forum posts.

.. code-block:: python

   import asyncio
   import os

   from loading_sdk import AsyncLoadingApiClient

   async def main():
       async with await AsyncLoadingApiClient(
           email=os.environ["LOADING_EMAIL"],
           password=os.environ["LOADING_PASSWORD"],
       ) as client:
           profile = await client.get_profile()
           print(profile["code"])

   asyncio.run(main())

.. toctree::
   :maxdepth: 2

   modules
