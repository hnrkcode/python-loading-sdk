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