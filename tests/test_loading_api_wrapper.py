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

    @patch("loading_api_wrapper.api.requests")
    def test_get_post_failure_empty_post_id(self, mock_requests):
        expected_response = {
            "code": 404,
            "message": '"post_id" is not allowed to be empty',
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_post("")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(
            response.get("message"), '"post_id" is not allowed to be empty'
        )
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_post_failure_post_does_not_exist(self, mock_requests):
        expected_response = {"code": 404, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_post("none_existing_post_id")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response.get("message"), "Post does not exist")
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_post_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "609f78fe90c3d5001e889e33",
                    "body": "Fota! Fota! Fota allihop! POKEMON! ",
                    "postType": "regular",
                    "createdAt": "2021-05-15T07:32:14.156Z",
                    "updatedAt": "2021-05-15T07:32:14.156Z",
                    "parentId": "609e2783b7a187001e0c0440",
                    "userId": "5d5948e1455110001e3f4d8b",
                    "replies": 0,
                }
            ],
            "users": [
                {
                    "id": "5d5948e1455110001e3f4d8b",
                    "name": "Wirus",
                    "picture": "f0e49672-ae24-4a68-a714-0f1165b69775.jpg",
                    "role": "user",
                    "createdAt": "2019-08-18T12:47:29.578Z",
                    "status": "active",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_post("none_existing_post_id")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("post"), expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5f9e4e8c2c32e2001ed17170",
                    "title": "Spelmusik samplad i låtar",
                    "body": "Har ni upptäckt några samples från spelmusik när ni suttit och lyssnat på ''vanlig'' musik?\n\nDela med er av era upptäckter!\n\nBörjar med en låt från den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat säkerställa det men visst måste väl det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\nÄr det även ljudeffekter från Link där vid 02:32, om jag hör rätt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget från Castlevania II. \nDet tog nästan pinsamt nog några genomlyssningar innan det klickade, låtarna har ju för fan samma namn också haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget från första Medal of Honor - Rjuken Sabotage. Denna var svårare, fick bara en känsla att den var från ett spel och sökte då upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2020-11-01T05:58:36.722Z",
                    "updatedAt": "2020-11-01T06:02:59.322Z",
                    "userId": "5bb80ac88fef22001d902d69",
                    "replies": 0,
                    "edits": 5,
                    "lastEdit": "2020-11-01T06:02:59.321Z",
                }
            ],
            "users": [
                {
                    "id": "5bb80ac88fef22001d902d69",
                    "name": "Twiggy",
                    "picture": "045d72f0-ce02-4613-99f1-c01c3b685cf4.jpg",
                    "role": "user",
                    "createdAt": "2018-10-06T01:07:20.176Z",
                    "status": "active",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("post"), expected_response)

        api = LoadingApiWrapper()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=0)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("post"), expected_response)

        api = LoadingApiWrapper()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=1)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("post"), expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_failure_empty_thread_id(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": '"thread_id" is not allowed to be empty',
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = None
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_failure_not_a_thread_id(self, mock_requests):
        status_code = 200
        expected_response = {
            "code": status_code,
            "message": "Exists, but was not a thread id",
        }
        regular_post = {
            "posts": [
                {
                    "id": "609ef4ee90c3d5001e889c5a",
                    "body": "Tror inte det bör vara helt omöjligt att typ köra mönster efter tredjedelar eller typ gyllene snittet. Ha olika ankarpunkter som betygen kan kretsa runt. Tänker dock att i en helt öppen lösning där bilder mest delas på internet så kommer graderingen göras helt i interagering med andra användare, låta det hela bli lite mer subjektivt, liksom.",
                    "postType": "regular",
                    "createdAt": "2021-05-14T22:08:46.301Z",
                    "updatedAt": "2021-05-14T22:08:46.301Z",
                    "parentId": "609e2783b7a187001e0c0440",
                    "userId": "5bb7aa868fef22001d902665",
                    "replies": 0,
                }
            ],
            "users": [
                {
                    "id": "5bb7aa868fef22001d902665",
                    "name": "Kiki",
                    "picture": "8b0e6e55-6b4a-4386-8551-e510b5e62fd4.png",
                    "role": "user",
                    "createdAt": "2018-10-05T18:16:38.350Z",
                    "status": "active",
                }
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = regular_post
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("609ef4ee90c3d5001e889c5a")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_failure_does_not_exist(self, mock_requests):
        status_code = 404
        expected_response = {"code": status_code, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("this_id_does_not_exist")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_failure_page_too_low(self, mock_requests):
        status_code = 200
        expected_response = {"code": 200, "post": {"posts": [], "users": []}}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {
            "posts": [
                {
                    "id": "5f9e4e8c2c32e2001ed17170",
                    "title": "Spelmusik samplad i låtar",
                    "body": "Har ni upptäckt några samples från spelmusik när ni suttit och lyssnat på ''vanlig'' musik?\n\nDela med er av era upptäckter!\n\nBörjar med en låt från den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat säkerställa det men visst måste väl det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\nÄr det även ljudeffekter från Link där vid 02:32, om jag hör rätt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget från Castlevania II. \nDet tog nästan pinsamt nog några genomlyssningar innan det klickade, låtarna har ju för fan samma namn också haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget från första Medal of Honor - Rjuken Sabotage. Denna var svårare, fick bara en känsla att den var från ett spel och sökte då upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2020-11-01T05:58:36.722Z",
                    "updatedAt": "2020-11-01T06:02:59.322Z",
                    "userId": "5bb80ac88fef22001d902d69",
                    "replies": 0,
                    "edits": 5,
                    "lastEdit": "2020-11-01T06:02:59.321Z",
                }
            ],
            "users": [
                {
                    "id": "5bb80ac88fef22001d902d69",
                    "name": "Twiggy",
                    "picture": "045d72f0-ce02-4613-99f1-c01c3b685cf4.jpg",
                    "role": "user",
                    "createdAt": "2018-10-06T01:07:20.176Z",
                    "status": "active",
                }
            ],
        }
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=-1)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response, expected_response)

    @patch("loading_api_wrapper.api.requests")
    def test_get_thread_failure_page_too_high(self, mock_requests):
        status_code = 200
        expected_response = {"code": 200, "post": {"posts": [], "users": []}}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {
            "posts": [
                {
                    "id": "5f9e4e8c2c32e2001ed17170",
                    "title": "Spelmusik samplad i låtar",
                    "body": "Har ni upptäckt några samples från spelmusik när ni suttit och lyssnat på ''vanlig'' musik?\n\nDela med er av era upptäckter!\n\nBörjar med en låt från den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat säkerställa det men visst måste väl det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\nÄr det även ljudeffekter från Link där vid 02:32, om jag hör rätt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget från Castlevania II. \nDet tog nästan pinsamt nog några genomlyssningar innan det klickade, låtarna har ju för fan samma namn också haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget från första Medal of Honor - Rjuken Sabotage. Denna var svårare, fick bara en känsla att den var från ett spel och sökte då upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2020-11-01T05:58:36.722Z",
                    "updatedAt": "2020-11-01T06:02:59.322Z",
                    "userId": "5bb80ac88fef22001d902d69",
                    "replies": 0,
                    "edits": 5,
                    "lastEdit": "2020-11-01T06:02:59.321Z",
                }
            ],
            "users": [
                {
                    "id": "5bb80ac88fef22001d902d69",
                    "name": "Twiggy",
                    "picture": "045d72f0-ce02-4613-99f1-c01c3b685cf4.jpg",
                    "role": "user",
                    "createdAt": "2018-10-06T01:07:20.176Z",
                    "status": "active",
                }
            ],
        }
        mock_requests.get.return_value = mock_response

        api = LoadingApiWrapper()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=2)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response, expected_response)
