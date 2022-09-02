import math
import aiohttp

from loading_sdk.settings import (
    API_URL,
    API_VERSION,
    EDITORIAL_POST_TYPES,
    EDITORIAL_SORT,
    USER_AGENT,
)


async def async_loading_api_client(email=None, password=None):
    client = AsyncLoadingApiClient()
    await client._set_cookie(email, password)

    return client


class AsyncLoadingApiClient:
    """
    An async client that allows python apps to easily communicate with the loading forums web api.

    Some methods can be used anonymously, while others require the client to be authenticated
    with user credentials.

    :param email: users email address (**optional**)
    :type email: str
    :param password: users password (**optional**)
    :type password: str
    """

    def __init__(self):
        self._cookies = None

    async def _set_cookie(self, email, password):
        if email and password:
            response = await self._authenticate(email, password)

            if response.get("code") == 200:
                self._cookies = response.get("cookies")

    async def _authenticate(self, email, password):
        url = f"{API_URL}/{API_VERSION}/auth/login"
        headers = {
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
        }
        data = {
            "email": email,
            "password": password,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    return {"code": response.status, "cookies": response.cookies}

                return await response.json()

    async def _get_threads_in_forum_category(self, category_name, page):
        url = f"{API_URL}/{API_VERSION}/posts/"
        headers = {"User-Agent": USER_AGENT, category_name: category_name}

        # Chooses a specific page instead of the first page which is the default page.
        if page and page > 1:
            headers["page"] = str(page)

        # Doing this checks to make sure it only return data from a page that exists.
        if page and page < 1:
            return {
                "code": 404,
                "message": "Page number too low",
                "data": {"posts": [], "users": []},
            }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                # Page out of range.
                if not data["posts"]:
                    return {
                        "code": 404,
                        "message": "Page number too high",
                        "data": data,
                    }

                return {
                    "code": response.status,
                    "message": "OK",
                    "data": data,
                }

    async def get_profile(self):
        """Returns authenticated users profile data

        :rtype: dict
        """

        url = f"{API_URL}/{API_VERSION}/users/profile"
        headers = {"User-Agent": USER_AGENT}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=headers, cookies=self._cookies
            ) as response:
                data = await response.json()

                if response.status == 200:
                    return {
                        "code": response.status,
                        "message": "OK",
                        "data": data,
                    }

                return data

    async def search(self, query):
        """Returns posts that matches the query

        :param query: Search query
        :type query: str
        :rtype: dict
        """

        url = f"{API_URL}/{API_VERSION}/search/"
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        data = {"query": query}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                data = await response.json()

                if response.status == 200:
                    return {
                        "code": response.status,
                        "message": "OK" if len(data["posts"]) else "No results",
                        "data": data,
                    }

                return data

    async def get_post(self, post_id):
        """Returns a specific post

        :param post_id: unique post id
        :type post_id: str
        :rtype: dict
        """

        if not post_id:
            return {"code": 404, "message": '"post_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{post_id}"
        headers = {"User-Agent": USER_AGENT}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if response.status == 200:
                    return {
                        "code": response.status,
                        "message": "OK",
                        "data": data,
                    }

                return data

    async def get_thread(self, thread_id, page=None):
        """Returns all posts on a specific page from a specific thread

        :param thread_id: unique thread_id
        :type thread_id: str
        :param page: thread page (**optional**)
        :type page: int
        :rtype: dict
        """

        if not thread_id:
            return {"code": 404, "message": '"thread_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{thread_id}"
        headers = {"User-Agent": USER_AGENT}

        # Chooses a specific page instead of the first page which is the default page.
        if page and page > 1:
            headers["page"] = str(page)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    return data

                if "title" not in data["posts"][-1]:
                    return {
                        "code": response.status,
                        "message": "Exists, but was not a thread id",
                    }

                # Doing this checks to make sure it only return data from a page that exists.
                if page:
                    replies = data["posts"][-1]["replies"]
                    pages = math.ceil(replies / 30)

                    # There is always atleast one page.
                    if pages == 0:
                        pages = 1

                    # Page is out of range.
                    if page < 1:
                        return {
                            "code": response.status,
                            "message": "Page number too low",
                            "data": {"posts": [], "users": []},
                        }

                    if page > pages:
                        return {
                            "code": response.status,
                            "message": "Page number too high",
                            "data": {"posts": [], "users": []},
                        }

                successful_response = {
                    "code": response.status,
                    "message": "OK",
                    "data": data,
                }

                return successful_response

    async def get_games(self, page=None):
        """Retruns threads from a specific page in the game category

        :param page: Game forum page
        :type page: int
        :rtype: dict
        """

        category_name = "games"
        thread_data = await self._get_threads_in_forum_category(category_name, page)

        return thread_data

    async def get_other(self, page=None):
        """Retruns threads from a specific page in the other category

        :param page: Other forum page
        :type page: int
        :rtype: dict
        """

        category_name = "other"
        thread_data = await self._get_threads_in_forum_category(category_name, page)

        return thread_data

    async def get_editorials(self, page=None, post_type=None, sort=None):
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

        url = f"{API_URL}/{API_VERSION}/posts/"
        headers = {
            "User-Agent": USER_AGENT,
            "texts": "texts",
            "post-type": "neRegular",
        }

        if post_type and post_type in EDITORIAL_POST_TYPES:
            headers["post-type"] = post_type

        if sort and sort in EDITORIAL_SORT:
            headers["sort"] = sort

        # Chooses a specific page instead of the first page which is the default page.
        if page and page > 1:
            headers["page"] = str(page)

        # Doing this checks to make sure it only return data from a page that exists.
        if page and page < 1:
            return {
                "code": 404,
                "message": "Page number too low",
                "data": {"posts": [], "users": []},
            }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()

                # Page out of range.
                if not data["posts"]:
                    return {
                        "code": 404,
                        "message": "Page number too high",
                        "data": data,
                    }

                return {
                    "code": response.status,
                    "message": "OK",
                    "data": data,
                }

    async def create_post(self, thread_id, message):
        """Create new post in a thread

        :param thread_id: Unique thread id
        :type thread_id: str
        :param message: Text that can be formatted with markdown that will be posted in the thread
        :type message: str
        :rtype: dict
        """

        if not thread_id:
            return {"code": 400, "message": '"thread_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{thread_id}"
        headers = {
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
        }
        data = {"body": message}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=data,
                cookies=self._cookies,
            ) as response:
                data = await response.json()

                # Has no auth token.
                if response.status == 401:
                    return data

                # Post id doesn't exist.
                if response.status == 404:
                    return data

                if response.status == 201:
                    return {
                        "code": response.status,
                        "message": "Post created",
                        "data": data,
                    }

                # Handle any other unknown status code.
                return data

    async def edit_post(self, post_id, message):
        """Edit existing post in a thread

        :param post_id: Unique post id
        :type post_id: str
        :param message: New text, that can be formatted with markdown,
            that will replace the old message
        :type message: str
        :rtype: dict
        """
        if not message:
            return {"code": 400, "message": '"message" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{post_id}"
        headers = {
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
        }
        data = {"body": message}

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                url,
                headers=headers,
                data=data,
                cookies=self._cookies,
            ) as response:
                data = await response.json()

                # Has no auth token.
                if response.status == 401:
                    return data

                # Post id doesn't exist.
                if response.status == 404:
                    return data

                if response.status == 200:
                    return {
                        "code": response.status,
                        "message": "Post updated",
                        "data": data,
                    }

                # Handle any other unknown status code.
                return data

    async def create_thread(self, title, message, category_name, post_type=None):
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
        if category_name not in ["games", "other"]:
            return {"code": 400, "message": "Invalid forum category"}

        if post_type and post_type not in EDITORIAL_POST_TYPES:
            return {"code": 400, "message": "Invalid post_type"}

        if not post_type:
            post_type = "regular"

        url = f"{API_URL}/{API_VERSION}/posts/"
        headers = {
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
        }
        data = {
            "category": category_name,
            "postType": post_type,
            "title": title,
            "body": message,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                data=data,
                cookies=self._cookies,
            ) as response:
                data = await response.json()

                # Validation errors. Happens when title or message is empty.
                # Possibly in other cases too.
                if response.status == 400:
                    return data

                # No auth token.
                if response.status == 401:
                    return data

                if response.status == 201:
                    return {
                        "code": response.status,
                        "message": "Thread created",
                        "data": data,
                    }

                # Handle any other unknown status code.
                return data

    async def edit_thread(self, thread_id, message):
        """Edit existing thread

        :param thread_id: Unique thread id
        :type thread_id: str
        :param message: New text, that can be formatted with markdown,
            that will replace the old message
        :type message: str
        :rtype: dict
        """

        thread_data = await self.edit_post(thread_id, message)

        if thread_data["code"] == 200:
            thread_data["message"] = "Thread updated"

        return thread_data
