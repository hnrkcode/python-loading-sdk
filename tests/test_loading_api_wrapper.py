import unittest
from unittest.mock import MagicMock, patch

import requests
from loading_api_wrapper import LoadingApiWrapper


class TestLoadingApiWrapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cookie_jar = requests.cookies.RequestsCookieJar()
        cls.cookie_jar.set("jwt", "placeholder_token_1")
        cls.cookie_jar.set("refreshToken", "placeholder_token_2")

    @patch("loading_api_wrapper.api.requests")
    def test_authenticate_success(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.cookies = self.cookie_jar

        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper("test@email.com", "password")

        self.assertEqual(api.cookies, self.cookie_jar)

        api = LoadingApiWrapper()
        response = api._authenticate("test@email.com", "password")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("cookies"), self.cookie_jar)

    @patch("loading_api_wrapper.api.requests")
    def test_authenticate_failure_incorrect_email_or_password(self, mock_requests):
        status_code = 401
        expected_response = {
            "code": status_code,
            "message": "Incorrect email or password",
        }
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response

        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper("incorrect@email.com", "incorrect_password")

        self.assertIsNone(api.cookies)

        api = LoadingApiWrapper()
        response = api._authenticate("incorrect@email.com", "incorrect_password")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 401)
        self.assertEqual(response.get("message"), "Incorrect email or password")

    @patch("loading_api_wrapper.api.requests")
    def test_authenticate_failure_invalid_email(self, mock_requests):
        status_code = 400
        expected_response = {
            "code": status_code,
            "message": "Validation error",
            "errors": [
                {
                    "field": "email",
                    "location": "body",
                    "messages": ['"email" must be a valid email'],
                    "types": ["string.email"],
                }
            ],
        }
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response

        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper("invalid_email_address", "password")

        self.assertIsNone(api.cookies)

        api = LoadingApiWrapper()
        response = api._authenticate("invalid_email_address", "password")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")

    @patch("loading_api_wrapper.api.requests")
    def test_authenticate_failure_empty_values(self, mock_requests):
        status_code = 400
        expected_response = {
            "code": status_code,
            "message": "Validation error",
            "errors": [
                {
                    "field": "email",
                    "location": "body",
                    "messages": [
                        '"email" is not allowed to be empty',
                        '"email" must be a valid email',
                    ],
                    "types": ["any.empty", "string.email"],
                },
                {
                    "field": "password",
                    "location": "body",
                    "messages": ['"password" is not allowed to be empty'],
                    "types": ["any.empty"],
                },
            ],
        }
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response

        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper("", "")

        self.assertIsNone(api.cookies)

        api = LoadingApiWrapper()
        response = api._authenticate("", "")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")

    @patch("loading_api_wrapper.api.LoadingApiWrapper._authenticate")
    @patch("loading_api_wrapper.api.requests")
    def test_get_profile_success(self, mock_requests, mock_authenticate):
        status_code = 200
        expected_response = {
            "id": "000000000000000000000000",
            "name": "test_username",
            "email": "test@email.com",
            "role": "user",
            "createdAt": "2022-01-01T00:00:00.000Z",
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiWrapper("test@email.com", "password")
        response = api.get_profile()

        self.assertIsNotNone(api.cookies)
        self.assertEqual(api.cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 200)
        self.assertDictEqual(response.get("profile"), expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_profile_failure(self, mock_requests):
        status_code = 401
        expected_response = {"code": status_code, "message": "No auth token"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response

        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_profile()

        self.assertIsNone(api.cookies)
        self.assertEqual(response.get("code"), 401)
        self.assertEqual(response.get("message"), "No auth token")

    @patch("loading_api_wrapper.api.requests")
    def test_search_success(self, mock_requests):
        expected_response = {
            "posts": [
                {
                    "parentId": "5c6d3faae34cd5001ddf33f4",
                    "body": "Är det bara jag som fått känslan av att Leia inte känner eller har träffat Obi-Wan i A New Hope? Hon verkar inte bry sig nämnvärt när han dör och mycket mindre än Luke, som känt honom i en halv kvart. I hennes meddelande i R2-D2 säger hon dessutom att det är hennes far som ber Obi-Wan att hjälpa henne, med repliker som låter som att hon inte har någon relation till honom. ",
                    "userId": "5bb76576066d1b001d5289f8",
                    "postType": "regular",
                    "replies": 0,
                    "createdAt": "2022-05-30T11:43:24.192Z",
                    "updatedAt": "2022-05-30T11:51:37.473Z",
                    "edits": 1,
                    "lastEdit": "2022-05-30T11:51:37.472Z",
                    "id": "6294addc119f1f6427cef2bb",
                }
            ],
            "users": [
                {
                    "id": "5bb76576066d1b001d5289f8",
                    "name": "Anders Eklöf",
                    "picture": "6efb2624-cf7b-402a-8834-f934f2c1c29b.jpg",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:21:58.857Z",
                    "status": "active",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.search("zGwszApFEcY")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("search_results"), expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_search_success_no_results(self, mock_requests):
        expected_response = {"posts": [], "users": []}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.search("zGwszApFEcYesf")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("search_results"), expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_search_failure_empty_query(self, mock_requests):
        status_code = 400
        expected_response = {
            "code": status_code,
            "message": "Validation error",
            "errors": [
                {
                    "field": "query",
                    "location": "body",
                    "messages": ['"query" is not allowed to be empty'],
                    "types": ["any.empty"],
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.search("")

        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")
        self.assertEqual(response, expected_response)
