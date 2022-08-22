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

    @patch("loading_api_wrapper.api.requests")
    def test_get_profile_success(self, mock_requests):
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

        with patch(
            "loading_api_wrapper.api.LoadingApiWrapper._authenticate"
        ) as mock_auth:
            mock_auth.return_value = {"code": 200, "cookies": self.cookie_jar}
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
