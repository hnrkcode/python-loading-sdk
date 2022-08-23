import math

import requests

API_URL = "https://api.loading.se"
API_VERSION = "v1"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"


class LoadingApiWrapper:
    def __init__(self, email=None, password=None):
        self.cookies = None

        if email and password:
            response = self._authenticate(email, password)

            if response.get("code") == 200:
                self.cookies = response.get("cookies")

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

    def get_profile(self):
        url = f"{API_URL}/{API_VERSION}/users/profile"
        headers = {
            "User-Agent": USER_AGENT,
        }
        response = requests.get(url, headers=headers, cookies=self.cookies)

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
        url = f"{API_URL}/{API_VERSION}/posts/"
        headers = {"User-Agent": USER_AGENT, "games": "games"}

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
