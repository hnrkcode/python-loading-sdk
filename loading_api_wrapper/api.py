import math

import requests

API_URL = "https://api.loading.se"
API_VERSION = "v1"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
EDITORIAL_POST_TYPES = [
    "neRegular",
    "review",
    "opinion",
    "update",
    "podcast",
    "conversation",
]
EDITORIAL_SORT = ["title"]


class LoadingApiWrapper:
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
        response = requests.post(url, headers=headers, data=data)

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
            return {"code": 404, "post": {"posts": [], "users": []}}

        response = requests.get(url, headers=headers)
        data = response.json()

        # Page out of range.
        if not len(data["posts"]):
            return {"code": 404, "post": data}

        return {"code": 200, "post": data}

    def get_profile(self):
        url = f"{API_URL}/{API_VERSION}/users/profile"
        headers = {
            "User-Agent": USER_AGENT,
        }
        response = requests.get(url, headers=headers, cookies=self._cookies)

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "profile": response.json(),
            }

        return response.json()

    def search(self, query):
        url = f"{API_URL}/{API_VERSION}/search/"
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        response = requests.post(url, headers=headers, data={"query": query})

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "search_results": response.json(),
            }

        return response.json()

    def get_post(self, post_id):
        if not post_id:
            return {"code": 404, "message": '"post_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{post_id}"
        headers = {
            "User-Agent": USER_AGENT,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return {
                "code": response.status_code,
                "post": response.json(),
            }

        return response.json()

    def get_thread(self, thread_id, page=None):
        """Returns post data if the id belongs to a thread start."""

        if not thread_id:
            return {"code": 404, "message": '"thread_id" is not allowed to be empty'}

        url = f"{API_URL}/{API_VERSION}/posts/{thread_id}"
        headers = {"User-Agent": USER_AGENT}

        # Chooses a specific page instead of the first page which is the default page.
        if page and page > 1:
            headers["page"] = str(page)

        response = requests.get(url, headers=headers)

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
            if page < 1 or page > pages:
                return {
                    "code": response.status_code,
                    "post": {"posts": [], "users": []},
                }

        successful_response = {"code": response.status_code, "post": data}

        return successful_response

    def get_games(self, page=None):
        category_name = "games"
        thread_data = self._get_threads_in_forum_category(category_name, page)

        return thread_data

    def get_other(self, page=None):
        category_name = "other"
        thread_data = self._get_threads_in_forum_category(category_name, page)

        return thread_data

    def get_editorials(self, page=None, post_type=None, sort=None):
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
            return {"code": 404, "post": {"posts": [], "users": []}}

        response = requests.get(url, headers=headers)
        data = response.json()

        # Page out of range.
        if not len(data["posts"]):
            return {"code": 404, "post": data}

        return {"code": 200, "post": data}

    def create_post(self, thread_id, message):
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
        response = requests.post(url, headers=headers, data=data, cookies=self._cookies)

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
        thread_data = self.edit_post(thread_id, message)

        if thread_data["code"] == 200:
            thread_data["message"] = "Thread updated"

        return thread_data
