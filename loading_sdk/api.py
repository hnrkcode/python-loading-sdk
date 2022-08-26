import math

import requests

from loading_sdk.settings import (
    API_URL,
    API_VERSION,
    EDITORIAL_POST_TYPES,
    EDITORIAL_SORT,
    USER_AGENT,
)


class LoadingApiClient:
    """A client that allows python apps to easily communicate with the loading forums web api.

    Some methods can be used anonymously, while others require the client to be authenticated
    with user credentials.

    :param email: users email address (**optional**)
    :type email: str
    :param password: users password (**optional**)
    :type password: str
    """

    def __init__(self, email=None, password=None):
        self._cookies = None

        if email and password:
            response = self._authenticate(email, password)

            if response.get("code") == 200:
                self._cookies = response.get("cookies")

    def _authenticate(self, email, password):
        url = f"{API_URL}/{API_VERSION}/auth/login"
        headers = {
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
        }
        data = {
            "email": email,
            "password": password,
        }
        response = requests.post(url, headers=headers, data=data, timeout=10)

        if response.status_code == 200:
            return {"code": 200, "cookies": response.cookies}

        return response.json()

    def _get_threads_in_forum_category(self, category_name, page):
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

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        # Page out of range.
        if not data["posts"]:
            return {"code": 404, "message": "Page number too high", "data": data}

        return {"code": 200, "message": "OK", "data": data}

    def get_profile(self):
        """Returns authenticated users profile data

        :rtype: dict
        """

        url = f"{API_URL}/{API_VERSION}/users/profile"
        headers = {
            "User-Agent": USER_AGENT,
        }
        response = requests.get(url, headers=headers, cookies=self._cookies, timeout=10)

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "message": "OK",
                "data": response.json(),
            }

        return response.json()

    def search(self, query):
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
        response = requests.post(
            url,
            headers=headers,
            data={"query": query},
            timeout=10,
        )
        data = response.json()

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "message": "OK" if len(data["posts"]) else "No results",
                "data": data,
            }

        return data

    def get_post(self, post_id):
        """Returns a specific post

        :param post_id: unique post id
        :type post_id: str
        :rtype: dict
        """

        if not post_id:
            return {"code": 404, "message": '"post_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{post_id}"
        headers = {
            "User-Agent": USER_AGENT,
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "message": "OK",
                "data": response.json(),
            }

        return response.json()

    def get_thread(self, thread_id, page=None):
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

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return response.json()

        data = response.json()

        if "title" not in data["posts"][-1]:
            return {
                "code": response.status_code,
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
                    "code": response.status_code,
                    "message": "Page number too low",
                    "data": {"posts": [], "users": []},
                }

            if page > pages:
                return {
                    "code": response.status_code,
                    "message": "Page number too high",
                    "data": {"posts": [], "users": []},
                }

        successful_response = {
            "code": response.status_code,
            "message": "OK",
            "data": data,
        }

        return successful_response

    def get_games(self, page=None):
        """Retruns threads from a specific page in the game category

        :param page: Game forum page
        :type page: int
        :rtype: dict
        """

        category_name = "games"
        thread_data = self._get_threads_in_forum_category(category_name, page)

        return thread_data

    def get_other(self, page=None):
        """Retruns threads from a specific page in the other category

        :param page: Other forum page
        :type page: int
        :rtype: dict
        """

        category_name = "other"
        thread_data = self._get_threads_in_forum_category(category_name, page)

        return thread_data

    def get_editorials(self, page=None, post_type=None, sort=None):
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

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        # Page out of range.
        if not data["posts"]:
            return {"code": 404, "message": "Page number too high", "data": data}

        return {"code": 200, "message": "OK", "data": data}

    def create_post(self, thread_id, message):
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
        response = requests.post(
            url,
            headers=headers,
            data=data,
            cookies=self._cookies,
            timeout=10,
        )

        # Has no auth token.
        if response.status_code == 401:
            return response.json()

        # Post id doesn't exist.
        if response.status_code == 404:
            return response.json()

        if response.status_code == 201:
            return {
                "code": response.status_code,
                "message": "Post created",
                "data": response.json(),
            }

        # Handle any other unknown status code.
        return response.json()

    def edit_post(self, post_id, message):
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
        response = requests.patch(
            url,
            headers=headers,
            data=data,
            cookies=self._cookies,
            timeout=10,
        )

        # Has no auth token.
        if response.status_code == 401:
            return response.json()

        # Post id doesn't exist.
        if response.status_code == 404:
            return response.json()

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "message": "Post updated",
                "data": response.json(),
            }

        # Handle any other unknown status code.
        return response.json()

    def create_thread(self, title, message, category_name, post_type=None):
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
        response = requests.post(
            url,
            headers=headers,
            data=data,
            cookies=self._cookies,
            timeout=10,
        )

        # Validation errors. Happens when title or message is empty. Possibly in other cases too.
        if response.status_code == 400:
            return response.json()

        # No auth token.
        if response.status_code == 401:
            return response.json()

        if response.status_code == 201:
            return {
                "code": response.status_code,
                "message": "Thread created",
                "data": response.json(),
            }

        # Handle any other unknown status code.
        return response.json()

    def edit_thread(self, thread_id, message):
        """Edit existing thread

        :param thread_id: Unique thread id
        :type thread_id: str
        :param message: New text, that can be formatted with markdown,
            that will replace the old message
        :type message: str
        :rtype: dict
        """

        thread_data = self.edit_post(thread_id, message)

        if thread_data["code"] == 200:
            thread_data["message"] = "Thread updated"

        return thread_data
