.. python-loading-sdk documentation master file, created by
   sphinx-quickstart on Thu Aug 25 20:46:11 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-loading-sdk's documentation!
==============================================

.. code-block:: python
   :caption: Simple example of how to use the SDK.

   from loading_sdk import LoadingApiClient

   # Creates a client that is authenticated with user credentials.
   client = LoadingApiClient(email="example@email.com", password="example_password")

   # Requires auth.
   profile_data = client.get_profile()
   print(profile_data)

   # Can be used anonymously.
   post_data = client.get_post(post_id="5bb7aac18fef22001d90267b")

   if post_data["message"] == "OK":
      print(f"post content: {post_data['data']['posts'][0]['body']}")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
