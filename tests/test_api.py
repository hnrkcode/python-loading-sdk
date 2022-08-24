import unittest
from unittest.mock import MagicMock, patch

import requests
from loading_sdk import LoadingApiClient


class TestLoadingApiClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cookie_jar = requests.cookies.RequestsCookieJar()
        cls.cookie_jar.set("jwt", "placeholder_token_1")
        cls.cookie_jar.set("refreshToken", "placeholder_token_2")

    @patch("loading_sdk.api.requests")
    def test_authenticate_success(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.cookies = self.cookie_jar

        mock_requests.post.return_value = mock_response

        api = LoadingApiClient("test@email.com", "password")

        self.assertEqual(api._cookies, self.cookie_jar)

        api = LoadingApiClient()
        response = api._authenticate("test@email.com", "password")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("cookies"), self.cookie_jar)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient("incorrect@email.com", "incorrect_password")

        self.assertIsNone(api._cookies)

        api = LoadingApiClient()
        response = api._authenticate("incorrect@email.com", "incorrect_password")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 401)
        self.assertEqual(response.get("message"), "Incorrect email or password")

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient("invalid_email_address", "password")

        self.assertIsNone(api._cookies)

        api = LoadingApiClient()
        response = api._authenticate("invalid_email_address", "password")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient("", "")

        self.assertIsNone(api._cookies)

        api = LoadingApiClient()
        response = api._authenticate("", "")

        self.assertDictEqual(response, expected_response)
        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient("test@email.com", "password")
        response = api.get_profile()

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertDictEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_profile_failure(self, mock_requests):
        status_code = 401
        expected_response = {"code": status_code, "message": "No auth token"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response

        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_profile()

        self.assertIsNone(api._cookies)
        self.assertEqual(response.get("code"), 401)
        self.assertEqual(response.get("message"), "No auth token")

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.search("zGwszApFEcY")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
    def test_search_success_no_results(self, mock_requests):
        expected_response = {"posts": [], "users": []}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiClient()
        response = api.search("zGwszApFEcYesf")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "No results")
        self.assertEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.search("")

        self.assertEqual(response.get("code"), 400)
        self.assertEqual(response.get("message"), "Validation error")
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_post_failure_empty_post_id(self, mock_requests):
        expected_response = {
            "code": 404,
            "message": '"post_id" is not allowed to be empty',
        }

        mock_response = MagicMock()
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_post("")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(
            response.get("message"), '"post_id" is not allowed to be empty'
        )
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_post_failure_post_does_not_exist(self, mock_requests):
        expected_response = {"code": 404, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_post("none_existing_post_id")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response.get("message"), "Post does not exist")
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.get_post("none_existing_post_id")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertEqual(response.get("data"), expected_response)

        api = LoadingApiClient()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=0)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertEqual(response.get("data"), expected_response)

        api = LoadingApiClient()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=1)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.get_thread("")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
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

        api = LoadingApiClient()
        response = api.get_thread("609ef4ee90c3d5001e889c5a")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_thread_failure_does_not_exist(self, mock_requests):
        status_code = 404
        expected_response = {"code": status_code, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_thread("this_id_does_not_exist")

        self.assertEqual(response.get("code"), 404)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_thread_failure_page_too_low(self, mock_requests):
        status_code = 200
        expected_response = {
            "code": 200,
            "message": "Page number too low",
            "data": {"posts": [], "users": []},
        }

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

        api = LoadingApiClient()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=-1)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_thread_failure_page_too_high(self, mock_requests):
        status_code = 200
        expected_response = {
            "code": 200,
            "message": "Page number too high",
            "data": {"posts": [], "users": []},
        }

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

        api = LoadingApiClient()
        response = api.get_thread("5f9e4e8c2c32e2001ed17170", page=2)

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "Page number too high")
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_games_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bb9c9911f1848001d97f202",
                    "title": "Ska spel problematisera sig själva?",
                    "body": '# S02A39 "Virtuell skräckstrategi"\n#### Aaron och Amanda får förstärkning från redaktionen i form av meriterade Alexander Rehnman samt VR-experterna Johan Lorentzon och Petter Arbman i veckans avsnitt!\n\n![bild](https://i.imgur.com/fdTxqmS.png)\n\nLoading är äntligen här!\n\nOch hur vill vi fira det på bästa sätt om inte genom att bjuda in Johan Lorentzon, Alexander Rehnman och Petter Arbman från redaktionen, för att snacka japansk kultur på 3DS och skräck-äventyr samt strategiskjutare i den virtuella verkligheten?\n\nAmanda reflekterar högt och lågt över Shadow of the Tomb Raider och Aaron över Forza Horizon 4 på ett sätt som gör att en funderar på om de båda inte har spelat något annat de senaste veckorna (Pst! Det har de ju nästan inte heller!).\n\nGlöm inte att svara på Veckans Fråga som denna veckan tar avstamp i vårt samtal runt Shadow of the Tomb Raider!\n##### "Är det bra att spel kommenterar på sin egen problematik?"\n#\nGÖR DIN RÖST HÖRD [HÄR!](https://polldaddy.com/poll/10129492/)\n#\n#\n\nHär hittar du TV-spelspodden:\n* [Twitter](https://twitter.com/TVspelspodden)\n* [Facebook](https://www.facebook.com/TVspelspodden/)\n* [Instagram](https://www.instagram.com/tvspelspodden/)\n* [Mail](mailto:info@tv-spelspodden.se)\n* [Arvik för samtliga avsnitt](http://tv-spelspodden.se/)\n* [Youtube](https://www.youtube.com/channel/UCh_NLZ9fbDFRk0zy8sq0Q3w?view_as=subscriber)\n* [Twitch](https://www.twitch.tv/tvspelspodden)\n\nPrenumerera:\n* [RSS-feed](http://tvspelspodden.libsyn.com/rss)\n* [iTunes](https://itunes.apple.com/se/podcast/tv-spelspodden/id1249509863?mt=2)',
                    "category": "games",
                    "coverImage": "https://i.imgur.com/fdTxqmS.png",
                    "postType": "conversation",
                    "createdAt": "2018-10-07T08:53:37.569Z",
                    "updatedAt": "2018-10-09T11:31:38.803Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 5,
                    "latestReply": "2018-10-09T11:31:38.788Z",
                    "latestReplyUserId": "5bb76b06066d1b001d528a04",
                },
                {
                    "id": "5bb9f0b71f1848001d97f2ed",
                    "title": "Vad VILL ni se härnäst från Rocksteady?",
                    "body": "Det har varit mycket surr om London-studion den senaste tiden. Allt från Batman till Harry Potter och TMNT. Men om vi slänger alla fakta ut genom fönstret och bara letar inom oss själva, vad VILL ni se härnäst från studion?",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-07T11:40:39.707Z",
                    "updatedAt": "2018-10-09T05:00:38.443Z",
                    "userId": "5bb9ef7d1f1848001d97f2e6",
                    "replies": 28,
                    "latestReply": "2018-10-09T05:00:38.441Z",
                    "latestReplyUserId": "5bb773d1066d1b001d528a17",
                },
                {
                    "id": "5bbba6cbf1deda001d33bcb7",
                    "title": "Ett spel. En dröm.",
                    "body": "Jag vaknar.\n\n..varmt..\n\nkollar på klockan\n\n..ångest..\n\nSluter ögonen\n\n..medelhavet..\n\nPlötsligt är jag där\n\nJag och mitt skepp på öppet hav\n\nPå väg\n\nPå äventyr\n\n..Kärlek..\n\nFint va?\n\nHar du drömt om tv-spel någon gång? ",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-08T18:49:47.717Z",
                    "updatedAt": "2018-10-08T23:22:19.726Z",
                    "userId": "5bb7af638fef22001d9027a4",
                    "replies": 18,
                    "latestReply": "2018-10-08T23:22:19.724Z",
                    "latestReplyUserId": "5bb7aa868fef22001d902665",
                },
                {
                    "id": "5bb87fdb8fef22001d902f6d",
                    "title": "Assassins Creed Odyssey [OT] This. Is. Sparta.",
                    "body": "![](https://i.imgur.com/CCBm7PS.jpg)\n![](https://i.imgur.com/mvKZqHj.jpg)\n![](https://i.imgur.com/VIlnqWr.jpg)\n![](https://i.imgur.com/mFRSE2d.jpg)\n![](https://i.imgur.com/EMyaX0n.jpg)\n![](https://i.imgur.com/3n4telH.jpg)\n\nMottagande\nIGN - 9.2/10\nGameSpot - 8/10\nDestructoid - 9/10\nEurogamer- Recommended\nGamInformer 8.25/10\nDualShockers 9/10\nTheSixthAxis - 8/10\nGamesRadar - 5/5\nTrustedReviews - 4/5\nGod is a Greek - 8/10",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-06T09:26:51.778Z",
                    "updatedAt": "2018-10-08T18:08:33.862Z",
                    "userId": "5bb77830066d1b001d528a1c",
                    "replies": 20,
                    "latestReply": "2018-10-08T18:08:33.860Z",
                    "latestReplyUserId": "5bb7d4628fef22001d902be9",
                },
                {
                    "id": "5bb9df1d1f1848001d97f294",
                    "title": "Skybound Games gör klart The Walking Dead",
                    "body": "[![](https://i.imgur.com/iHsmpzJ.jpg)](https://twitter.com/skyboundgames/status/1048735364452634626)",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-07T10:25:33.392Z",
                    "updatedAt": "2018-10-08T17:14:43.243Z",
                    "userId": "5bb7abbb8fef22001d9026c9",
                    "replies": 12,
                    "latestReply": "2018-10-08T17:14:43.241Z",
                    "latestReplyUserId": "5bb7d5f68fef22001d902c01",
                },
                {
                    "id": "5bb79b58066d1b001d528a47",
                    "title": "Forza Horizon 4, av Douglas Lindberg",
                    "body": "# Douglas Lindberg recenserar Forza Horizon 4\n#### Xbox One\n\n![F1](https://i.imgur.com/FidNKS5.png)\n\nForza Horizon har alltid legat mig varmt om hjärtat. Jag minns fortfarande när det första spelet släpptes och vilken kontrast det var mot de mer seriösa Motorsport-utgåvorna. \n\nDet var sex år sen. \n\nOch nu när det fjärde spelet i serien är här så är det svårt att inte imponeras av den relevans som serien fortfarande har.\n\nForza Horizon 4 är en arkadracer som utspelar sig i en öppen värld med mängder av tävlingar, utmaningar och hemligheter att upptäcka. Prestationer ger dig erfarenhet och erfarenhet ger dig belöningar i form av nya bilar. Just den här upplagan innehåller ungefär 450 stycken vilket bör räcka för att hålla en sysselsatt ett tag framöver.\n\nSpelet är överlag väldigt likt sina föregångare, men det finns en del system som är förändrade. Skill points är exempelvis bundna till bilarna istället för till din karaktär, alla events kan köras solo eller i co-op med andra och nya tävlingar låses upp när du samlar erfarenhet i varje enskild kategori. Kör du till exempel banrace låser du upp nya banrace och inget annat. \n\nOm de här systemen är bättre eller sämre än förut är en smaksak. Det nya upplägget ger åtminstone en fräsch prägel åt konceptet Horizon som i övrigt inte skiljer sig särskilt mycket från förut. \n\nUtvecklarna av spelet, Playground Games, har lagt fokus på flödet i spelet vilket märks tydligt. Det finns inga startsekvenser, laddningstiderna är minimala och världen är härligt komprimerad vilket gör att nästa tävling alltid finns en kort startsträcka ifrån dig. Det här skiljer sig åt en aning från Forza Horizon 3 som hade en mer utspridd spelplats. Fyrans kompakthet bidrar istället till en mer inbjudande upplevelse där spelet aldrig står still, utan allting flyter ihop från den ena utmaningen till det andra. \n\nÖverlag är tävlingarna logiskt indelade. Du har dina tävlingar på landsväg, på skogsväg och över landskap utan väg. Lägg där till fartkameror, hopp och driftzoner och du har ditt klassiska Horizon-paket. Utöver det här har utvecklarna också valt att lägga in särskilda story-uppdrag, en evolution av tidigare Bucket List-uppdrag. Dessa uppdrag erbjuder specifika utmaningar i specifika miljöer. Där till exempel vissa handlar om att köra för en driftklubb och sladda runt i särskilda superbilar medan andra story-uppdrag till exempel handlar om att köra som en stuntförare i filminspelningar. Det här är ett intressant koncept som kommer utvecklas under året. \n\nDet är också med alla de här tävlingarna som Forza Horizon 4 blir intressant. \n\nFör till skillnad från sina föregångare har utvecklarna den här gången valt att uppdatera spelet under årets gång. Det kommer innebära innehåll i form av nya tävlingar, nya bilar och nya utmaningar varje vecka. Ett koncept vi sett i så många andra spel den senaste tiden.\n\nForza Horizon 4 har dock ett grepp som gör spelet unikt. \n\nFör när innehållet uppdateras förändras även årstiden vilket är den enskilt största nyheten för Horizon som spel. \n\nVarje torsdag förändras klimatet från sommar till höst, från höst till vinter och så vidare. Ni förstår hur årstider fungerar. Dessa ligger sedan på månadscykler så ett år i spelvärlden är en månad i verklig tid. \n\n![F1](https://i.imgur.com/PrA9A3V.png)\n\nDet här är något som ska bli intressant att följa eftersom det ger en anledningar att alltid komma tillbaka till spelvärlden för att jaga nya belöningar då det kommer finnas event som är specifika för varje enskild årstid. Min förhoppning är att detta blir inspirerande snarare än ännu en syssla i våra redan pressade spelscheman.\n\nMed årstiderna kommer också olika väder som påverkar förutsättningarna. En regnig bana på hösten körs annorlunda från en torr på sommaren. Hösten är kall och geggig medan sommaren ger varmare vägbanor för högre hastigheter. Logiskt liksom. Och det känns smått fantastiskt att den nuvarande generationens spel uppfyller sådant som vi tidigare bara kunde drömma om.\n\nForza Horizon 4 utspelar sig i Skottland och landskapet är ingenting annat än spektakulärt. Höga berg, djupa dalar, bäckar, skogar, stenar, städer, landsbygd, slott, torp och gruvor. Horizon-serien har hittat hem och det finns så mycket detaljer i allt att spelet nästan övertrumfar verkligheten. Det är så pass personligt och nära att det nästan blir lite jobbigt att förstöra någons utemöbler i deras alldeles för fina trädgård. Men jag gör det ändå för jag måste samla de samlingsbara objekten som finns gömda i världen. Lägg till de fyra årstiderna på allt det här och du har fyra olika spelvärldar i en. \n\nDet är ingenting annat än magnifikt.\n\nEn annan nyhet för serien är också din karaktär som du kan göra personlig med hjälp av kläder, accessoarer och emotes. Karaktären blir din avatar och jag upplever den vara minst lika mycket i fokus som de bilar du kör. Det här känns igen från spel som till exempel Fortnite och det märks att Forza Horizon 4 är inspirerat av samtiden. \n\nInte mig emot. \n\nFyran har också ändrat upplägget med samlingsplatser för spelarna. Istället för hub-festivaler finns det nu bara en festival i världen och du som spelare bor istället i små söta hus som finns utspridda över den brittiska landsbygden, vilket inte är en jättedum idé för att göra spelet mer jordnära. \n\nDe här nyheterna ger personlighet åt en serie som tidigare mest handlat om överdrivet välrenderade bilar på vattenblanka landsvägar. Nu är det inbjudande på ytterligare sätt.\n\nRent prestandamässigt upplever jag det vara något laggigt på första generationens Xbox One. Men jag har spelat med folk som använt PC, Xbox One S och Xbox One X och de säger att det inte är något annat än fantastiskt. Och allt eftersom jag tagit mig längre in i spelet så märker även jag av flytet och den sagolika grafiken. Fyran är väldigt lik trean rent grafiskt och optimeringen är inget annat än fenomenal. Några dippar i bilduppdateringen kan inträffa, men annars fungerar det helt fläckfritt.\n\nStyrkan i spelet är fortfarande känslan av att ständigt uppnå någonting där hemligheten ligger i den fina balansen mellan krav och belöning. Det är mer av samma och har du spelat ett tidigare spel så vet du exakt vad du har att förvänta dig. \n\nForza Horizon 4 känns också som ett spel som för serien i en positiv riktning där det fanns en risk allting skulle stagnera. Istället tar Horizon-serien ny kraft och skickar det vidare mot nya höjder. Jag ser redan fram emot ett femte spel och då är jag inte ens på långa vägar klar med det här. Det om något är ett gott betyg för nutidens bästa arkadracer.\n",
                    "category": "games",
                    "coverImage": "https://i.imgur.com/FidNKS5.png",
                    "postType": "review",
                    "createdAt": "2018-10-05T17:11:52.246Z",
                    "updatedAt": "2018-10-08T13:01:02.142Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 15,
                    "latestReply": "2018-10-08T13:01:02.140Z",
                    "latestReplyUserId": "5bb75ec2066d1b001d5289e9",
                },
                {
                    "id": "5bb8df9e8fef22001d9031f9",
                    "title": "Spelkompositören Ben Dalglish död. ",
                    "body": "En av de stora kompositörerna under 8 och 16-bit eran har dött.\nBen Dalglish blev 52 år och skrev mycket musik för bland annat C64, däribland The Last Ninja, Switchblade, Krakout och Gauntlet.\n\nhttps://sv.wikipedia.org/wiki/Ben_Daglish\nhttps://youtu.be/hF9mwPUY6b4\n\nhttps://youtu.be/m_Wnt58xeXM\nHttps://youtu.be/OUyGpp6_qA4\n",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-06T16:15:26.761Z",
                    "updatedAt": "2018-10-08T05:54:16.144Z",
                    "userId": "5bb7ad278fef22001d902723",
                    "replies": 11,
                    "latestReply": "2018-10-08T05:54:16.141Z",
                    "latestReplyUserId": "5bb7e8478fef22001d902cd5",
                },
                {
                    "id": "5bb7fbde8fef22001d902d4d",
                    "title": "Gratis spel",
                    "body": "Tänkte bara tipsa om att Shadow warrior 2 är gratis på Gog för tillfället",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-06T00:03:42.225Z",
                    "updatedAt": "2018-10-07T20:42:58.249Z",
                    "userId": "5bb7fa1b8fef22001d902d40",
                    "replies": 2,
                    "latestReply": "2018-10-07T20:42:58.246Z",
                    "latestReplyUserId": "5bb7a9cc8fef22001d9025ef",
                },
                {
                    "id": "5bba67e0e36d9a001d2fc370",
                    "title": "Importhjälp",
                    "body": "Det har råkat bli så att jag kommit över några japanska spel, de är ju väldigt billiga, och så länge det inte rör sig om texttunga spel brukar det ju gå att spela alldeles utmärkt utanför menyerna.\nHar därför börjat snegla lite på japanska enheter för att kunna spela de här spelen optimalt. Har testat lite med konverterare, men de är rätt kinkiga med om de fungerar och kan ge lite mystiska fel ibland eller märkliga överföringar i upplösning och hz.\n\nSneglar extra mycket på en japansk Gamecube, Mega Drive och Super Famicom, men hur är det med att spela sådana här i Sverige? Kan man använda svenska kablar för ström? Har de samma standard för bildsladdarna? Måste jag använda japanska diton med omvandlare påkopplade?\n\nVill ju kunna spela, men inte finna att jag måste få tag i en gammal Japan-utvecklat tjock-TV eller råkar bränne ner huset för att strömomvandlingen blev fel.",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-07T20:09:04.905Z",
                    "updatedAt": "2018-10-07T20:37:47.712Z",
                    "userId": "5bb7aa868fef22001d902665",
                    "replies": 6,
                    "latestReply": "2018-10-07T20:37:47.708Z",
                    "latestReplyUserId": "5bb7af388fef22001d90279a",
                },
                {
                    "id": "5bba53c9e36d9a001d2fc2d4",
                    "title": "New 2ds säljes",
                    "body": "Finns det något intresse av att ha en 2ds i dagens switch landskap? Jag köpte maskinen förra året och den är ytterst sparsamt använd. Vit och orange i färg. 32gb minneskort med pokemon sun.\n999kr",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-07T18:43:21.363Z",
                    "updatedAt": "2018-10-07T18:43:21.363Z",
                    "userId": "5bb7b5768fef22001d9028ea",
                    "replies": 0,
                },
                {
                    "id": "5bb889dd8fef22001d902fce",
                    "title": "Super Mario Party säljes.",
                    "body": "Endast provspelat.\n\n480:-\n\nSka det skickas står jag för frakten.\n\nEj intresserad av byten.",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-06T10:09:33.930Z",
                    "updatedAt": "2018-10-07T12:28:38.771Z",
                    "userId": "5bb7de268fef22001d902c83",
                    "replies": 1,
                    "latestReply": "2018-10-07T12:28:38.764Z",
                    "latestReplyUserId": "5bb7de268fef22001d902c83",
                },
                {
                    "id": "5bb89dcf8fef22001d903044",
                    "title": "Officiella tråden: Köpa billiga spel",
                    "body": "En av mina favorit trådar på loading var när folk tipsade om billiga spel eller spel som helt enkelt var gratis.\n\nTips om billiga spel blev bannat från köp och sälj tråden så tänkte att jag skapar en för bara det här ändamålet.\n\nRegler: Du får tipsa om allt som är spelrelaterat, spel, konsoler, handkontroller och liknande.\n\nDet får vara sänkta priser, bra bundles, spel som är gratis via tex humble bundle. Så länge Der är spel är det tillåtet. ",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-06T11:34:39.925Z",
                    "updatedAt": "2018-10-06T16:49:20.686Z",
                    "userId": "5bb89a1b8fef22001d90302c",
                    "replies": 3,
                    "latestReply": "2018-10-06T16:49:20.683Z",
                    "latestReplyUserId": "5bb7ad278fef22001d902723",
                },
                {
                    "id": "5bb78ab8066d1b001d528a2e",
                    "title": "Shadow of the Tomb Raider, av Aaron Vesterberg Ringhög",
                    "body": "# Aaron Vesterberg Ringhög testar Shadow of the Tomb Raider\n#### Laras osäkerhet kan vara precis vad genren behöver.\n\n![Lara Croft](https://images-eds-ssl.xboxlive.com/image?url=8Oaj9Ryq1G1_p3lLnXlsaZgGzAie6Mnu24_PawYuDYIoH77pJ.X5Z.MqQPibUVTcP27a0swKxkIXgb1dv4AtqI4XCXnM0hQ1dfBILJxUZy.Hmu3.2jPm97NlZGozQg9dYtTqOEeewNOxcleTNZm42JMWV3qfcYU3RP838p2RCm6RuHW.i9edsrfwVdyT_fxRIJ4LL0Bw4TPAKQsV9mCZeBucHTGDX9vEiH2ZO_ixlNw-&h=1080&w=1920&format=jpg)\n\nI slutet av maj bjöds jag in till Square Enix i London för att få lägga vantarna på ett demo av Shadow of the Tomb Raider. I dryga 40 minuter fick jag sitta med en version av spelet rullandes på en Xbox One X följt av en kvart tillsammans med Jill Murray (manusförfattare). Vad jag fick uppleva är måhända inte representativt för ett spel som mycket väl kan ta tiotals timmar att ta mig igenom, men kanske allra mest en känsla av medvetenhet som jag inte skådat sedan serien först tog sin plats hos miljontals spelare världen över. Känslan av osäkerhet hos vår kära protagonist. En känsla jag hoppas få djupdyka i ännu mer när spelet väl släpps den 14 september i år. \n\nLåt mig förklara.\n\nShadow of the Tomb Raider utspelar sig i Sydamerika bland vad som är kraftigt influerat av både inka- och mayafolkets kulturella miljöarv. Trinity är tillbaka som ansikte för den giriga organisationen vars främsta mål är att … ja, vad är egentligen Trinitys mål? Är de ute efter världsherravälde eller står de egentligen för något större? Något som Lara ännu inte lyckats omfamna med sitt ständiga fokus på att skydda antikens reliker från de onda herrarna i helikoptrar?\n\nFrågor som dessa är, på ett nästan chockerande sätt, centrala i de 40 minuter jag får med Lara. Att gå in på mer narrativa sekvenser är därför nödvändigt för att min poäng ska nå hela vägen fram, men först en liten överblick över vad jag fick uppleva.\n\nI demot får jag ta mig an fyra separata delar. Ett moment där mitt uppdrag är att utforska Laras nya förmågor på slagfältet, ett annat där jag spionerar på en person från Trinity genom Mexicos festivalpyntade smågator under de dödas dag, en gravplundring som slutar i en mer scriptad sekvens där Lara löper för sitt liv medan allt fallerar omkring henne samt en promenad genom den gömda staden Paititi.\n\nNär det kommer till striderna är det direkt uppenbart att Shadow of the Tomb Raider inte är ett spel där det går att spela som pacifist. Även om jag försöker springa, alternativt smyga genom en miljö full av fiender, slutar det tyvärr ändå alltid på samma sätt. Någon stackare noterar mig och vips pannkaka är jag illa tvungen att ha ihjäl både honom och alla hans kollegor. En efter en.\n\nLara har sannerligen blivit den typen av råskinn hon en gång i tiden flydde ifrån. \n\nFör oss som spelat de tidigare spelen är hennes rörelseschema precis som vi minns, även om Lara nu ges fler möjligheter och verktyg att använda medan hon tar kål på sina fiender. Hon tar sig an sina offer från trädens kronor, från leriga diken och snåriga buskage som om hon aldrig gjort annat. Och inte en enda gång ropar någon “Mördare!” efter henne. \n\nBara en sån sak.\n\nJag kan bara hoppas på att det kommer tillföra någon form av dynamik till berättelsen Eidos Montreal vill förmedla i och med den tredje installationen av Tomb Raiders pånyttfödelse. För det finns ändå något där, det gör det verkligen. Låt mig återkomma till det här om en liten stund.\n\nVad gäller de nya grottorna och pusslen som medföljer kan jag egentligen inte säga så mycket eftersom det område vi fick spela på plats var av i princip samma karaktär som i tidigare installationer. Fysikpussel som löses genom att Lara tar sig runt bland väggar och över farliga stup för att dra i spak A och sedan knuffa stenbumling B, för att sedan öppna dörr C. Att Eidos förvisso lovar större och mer utmanande pussel än någonsin tidigare får helt enkelt ses som en rejäl morot för oss som söker oss till genren av just den anledningen. Men i mångt och mycket är upplevelsen ändå mer av samma. På gott och ont.\n\nPaititi som kommer fungera som en central hubb för spelet är däremot väldigt intressant. En hemlig stad (japp, det finns en till tydligen) fylld av invånare som lever sina egna liv, med sina egna behov och mål, där Lara kan ta sig an både primära och sekundära uppdrag genom att samtala med utvalda invånare i staden. Den initiala känslan jag får när jag promenerar runt bland butiker och invånare är som direkt hämtad från våra mer traditionellt stöpta rollspelsstäder. Jag kan nästan ana hur Eidos Montreal med sin erfarenhet från framför allt Deus Ex-spelen på senare år har velat ta Tomb Raider vidare ut i okända träskmarker. Både i form av den öppna världen, men återigen, kanske framför allt via berättelsen.\n\nOch det är hit jag vill komma.\n\nEn känsla av medvetenhet blir plötsligt ytterst välkommen i en genre som oftast faller platt till förmån för den klassiska “white savior”-tropen som varit alltför tydligt etablerad ända sedan vi fick se en ung Harrison Ford rädda antika kulturella arv från ondingar vars enda mål är världsherravälde (om inte tidigare). Att Lara Croft, Nathan Drake och nämnda doktor Jones sedan urminnes tider själva tagit sig rätten att gräva upp kulturföremål utan de rättmätiga arvingarnas samtycke är ju trots allt ett populärkulturellt problem även spelmediet fått dras med till denna dag. Därför tycker jag att det känns som ett steg i rätt riktning att få åtminstone en liten hint om vad Lara ställs inför i en av sekvenserna jag fick spela.\n\nMindre spoilers kommer i följande stycke.\n\n![Lara Croft](https://media.playstation.com/is/image/SCEA/shadow-of-the-tomb-raider-screen-08-ps4-us-27apr18?$MediaCarousel_Original$)\n\nI slutet av demot har Lara nämligen precis lyckats få tag i en relik som ska vara avgörande för inte bara folket i den mexikanska byn hon befinner sig i, utan även resten av världen. Hon finner sig dock snabbt tillfångatagen av Trinity och under följande meningsutbyte mellan Lara och en av Trinitys ledare, doktor Dominguez, får hon snabbt insikten om att saker och ting inte riktigt är som hon från början trodde. Dominguez frågar nämligen om reliken hon fick med sig var allt hon hade fått med sig och när Lara visar att hon inte har den blekaste aning om vad han pratar om kommer det. Dominguez beordrar snabbt sina mannar med nästan övertydlig desperation i rösten att släppa henne, innan han beger sig av i en helikopter bara för att lämna en oförstående Lara ensam kvar.\n\nI vad som inte kan vara mer än en sekund hinner jag gå från att se Lara som en stark och målmedveten hjältinna, till något, nästan smärtsamt mänskligt.\n\nLara, precis som jag, blir mållös.\n\nVad som följer är inget mindre än en katastrof. Laras handlingar har nu utlöst vad som närmast kan likna en apokalyps och innan hon hunnit greppa vad som precis har hänt, väller en flodvåg in över en närliggande by som bokstavligen talat går under. Människor flyr sina hus och skriker i förtvivlan medan deras närmaste omkommer i den enorma flodvågen. I en explosiv sekvens springer Lara för sitt liv över rasande husfasader, under elstolpar som faller samman och hamnar till slut klättrandes uppför en husvägg när hon ser en liten pojke som hänger dinglandes ovanför en säker död.\n\nJag klättrar närmare och är precis på väg att ta mig fram till den skrikande pojken när fästet släpper och överlåter pojken till sitt grymma öde.\n\nBorta. Ingen “du har misslyckats-skärm” eller omladdning till samma sekvens. Utan bara …\n\n...borta.\n\nEfter att jag tagit mig upp på ett av hustaken som fortfarande står upp träffar Lara sin vän Jonah. Här inträffar nu ett replikskifte som verkligen ger mig förhoppningar om att Eidos Montreal har vågat utveckla Laras karaktär till en nivå serien verkligen behöver. För medan Lara fortsätter ha uppfattningen om att Trinitys enda roll i det stora hela är deras  inblandning i hennes fars död och allt det hemska som pågår, stannar plötsligt Jonah upp henne och säger något som känns äkta och genuint.\n\nHan tar ner Lara på jorden. Laras jakt efter Trinity är inte längre vad som är viktigast. Laras ego träder fram som en rak höger i kölvattnet av alla de människorna som fått sätta livet till på grund av hennes framfart.\n\nLaras nästan totala oförstånd inför vad hon själv har varit med och skapat blir inte bara effektivt rent narrativt, utan också ett oerhört skickligt hantverk i att ifrågasätta protagonistens egen agenda, tillika min som spelare. Att Lara kan bära en hel bys ödeläggelse på sina axlar öppnar givetvis upp för en väldigt dynamisk karaktärsutveckling hos en protagonist som vi lärt känna som en rättvis och hedersam karaktär. Och om det är något jag vill se mer av så är det utan tvekan just det här.\n\nIfrågasättanden. Inte bara över Laras roll som gravplundrare av reliker, utan också som person.\n\nOch det, om något - vill jag verkligen få utforska mer.",
                    "category": "games",
                    "coverImage": "https://images-eds-ssl.xboxlive.com/image?url=8Oaj9Ryq1G1_p3lLnXlsaZgGzAie6Mnu24_PawYuDYIoH77pJ.X5Z.MqQPibUVTcP27a0swKxkIXgb1dv4AtqI4XCXnM0hQ1dfBILJxUZy.Hmu3.2jPm97NlZGozQg9dYtTqOEeewNOxcleTNZm42JMWV3qfcYU3RP838p2RCm6RuHW.i9edsrfwVdyT_fxRIJ4LL0Bw4TPAKQsV9mCZeBucHTGDX9vEiH2ZO_ixlNw-&h=1080&w=1920&format=jpg",
                    "postType": "opinion",
                    "createdAt": "2018-10-05T16:00:56.156Z",
                    "updatedAt": "2018-10-06T09:31:38.598Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 10,
                    "latestReply": "2018-10-06T09:31:38.596Z",
                    "latestReplyUserId": "5bb7ac428fef22001d9026ea",
                },
                {
                    "id": "5bb7ce278fef22001d902b7b",
                    "title": "Är på jakt efter platinum",
                    "body": "Har inte fått platinum på LÄNGE, jag blir tokig. Snälla rekommendera ett spel som ger lätt platinum!!!!!!!!!!!!!!!!!!!!!",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-05T20:48:39.951Z",
                    "updatedAt": "2018-10-06T08:02:14.567Z",
                    "userId": "5bb7cd3a8fef22001d902b61",
                    "replies": 12,
                    "latestReply": "2018-10-06T08:02:14.561Z",
                    "latestReplyUserId": "5bb86bda8fef22001d902ea2",
                },
                {
                    "id": "5bb782d2066d1b001d528a25",
                    "title": "Shenmue I & II, av Aleksandar Buntic",
                    "body": "# Aleksandar Buntic recenserar Shenmue 1 och 2\n#### Playstation 4\n\n![Shenmue I & II](http://images.pushsquare.com/news/2018/04/soapbox_why_you_should_play_shenmue_i_and_ii_on_ps4/attachment/0/original.jpg)\n\n1998 släppte Sega sin sista spelkonsol. Dreamcast är en spelkonsol jag aldrig själv ägt utan fått ta del av genom ett fåtal vänner. Jag minns så väl första gången jag fick reda på att den ens fanns. Min kompis som hade skilda föräldrar bjöd hem mig till hans pappa för första gången och på hans rum stod en underlig maskin. På skärmen syntes figurer som jag kände igen sen tidigare. Sonic och kompani. Det var första gången jag fick uppleva Sonic Adventure, Crazy Taxi, Samba de Amigo och det skulle ta flera år efter den upplevelsen innan jag fick uppleva Dreamcast igen. Det har alltid funnits en spelserie i Dreamcasts bibliotek som jag varit intresserad av.\n\nShenmue.\n\nDet tar inte lång tid innan jag förstår hur stort och ambitiöst projekt Shenmue var för tiden. Spelet innehåller stora öppna ytor, mängder med inspelade dialoger, unika interaktioner med väldetaljerade objekt i världen och ett avancerat stridssystem som tidigare använts i Virtua Fighter-serien. Det är också det spelet som vi har att skylla på för det förbaskade systemet som heter Quick Time Events (okej, det kan funka i vissa typer av spel).  \n\nFörsta delen i äventyret som är Shenmue känns ganska hoppigt i sin progression. Visst, det finns en struktur där, men det dyker upp många stoppklossar på vägen. Spelet börjar med att din far blir dödad av Lan Di, en mystisk man som vill åt en speciell spegel. Resten av spelet går ut på att försöka samla ihop information om Lan Di och hans kompanjoner. \n\nVärlden öppnar upp sig och jag har enbart det som mål. Inga direkta markörer eller vettiga ledtrådar. Jag vandrar runt i staden och pratar med människor. Ställer olika frågor och får olika svar. Ibland kan svaren vara väsentliga för äventyret, men ibland är svaret så fragmenterat att man måste fråga runt om den nya informationen. Jag tror jag börjar förstå vad Metallicas låt “Nothing Else Matters” handlar om . Ni vet: “So close, no matter how far…”. De olika karaktärerna som befolkar staden är väldigt varma. De vill gärna hjälpa till och det känns verkligen som en gemenskap. Det är synd att man inte får mer inblick i deras värld. Jag hade velat veta mer om “amerikanen” (alla amerikaner pratar engelska med japansk brytning) Tom Johnson som säljer korvar i sin foodtruck. Eller om Shiro Kurita som är besatt av allt som har med militären att göra. Shenmue är en personlig resa om Ryo Hazukis öde och jakten på hämnd. \n\nSpelet känns som en smått snabbspolad och begränsad version av verkliga livet. Den känslan förstärks verkligen av hur pass viktig tiden är i spelet. Under vissa skeden av spelet var jag tvungen att vänta på att tiden skulle passera ett visst klockslag innan jag kunde ta del av nästa del av berättelsen. Tiden är en otroligt intressant aspekt i spelet som på ett sätt gör spelet mer levande, men samtidigt gör det även progressionen mer travande. Det fanns stunder då jag kände att det var smått frustrerande, då jag bara ville få fortsätta uppleva berättelsen. Visst, det finns andra saker man kan göra i spelet för att få tiden att gå. Det går till exempel att gå till arkaden och spela gamla klassiska spel som Space Harrier. Det går även att göra några av de små sidouppdragen. Sedan finns det en hel del samlarobjekt som man kan försöka samla alla av. För mig personligen blev det tillfällen då jag släppte kontrollen och satte mig och gjorde annat medan jag väntade på att tiden skulle gå. Och det är något jag egentligen är helt okej med. Det förstörde inte min upplevelse av spelet som helhet, men det kräver ändå att man är villig och har tålamod. \n\nPengar blir vid ett senare tillfälle också en viktig del i spelet. För att kunna ta sig vidare måste jag jobba ihop pengar genom att transportera lådor med gaffeltruck. Det är ett heltidsjobb där man mellan passen får en timmes lunch. Denna delen av spelet är väldigt monoton och tar upp alldeles för mycket av spelets slutfas. \n\nNågot som verkligen är unikt för tiden är hur många olika objekt i världen man kan interagera med. Det går i stort sett att öppna varenda liten lucka eller låda och i många fall går det även att lyfta upp saker som finns i lådorna för en närmare titt. När man passerar stadens byggnader går det även att zooma in på gatunummer och skyltar. Oftast är denna funktion helt överflödig för att föra berättelsen framåt, men den gör ändå mycket för inlevelsen och trovärdigheten av världen.\n\nI Shenmue 2 har vi bytt miljö från den hemtrevliga staden Yokosuka till främmande och smått förvirrande distriktet Wan Chai i Hong Kong. Vi är inte längre en del av gemenskapen, vi är främlingar i ett annat land. Vi har ingenstans att sova och knappt några pengar att leva på. Det är en känsla som verkligen formar Shenmue 2 som upplevelse. Det finns såklart fortfarande vänliga personer, men de flesta invånare man stöter på är mer stressade och kräver ofta mer i gengäld. Dessutom är det fler gäng som agerar öppet på gatan och runt varje hörn kan man hitta hasardspel i form av “Lucky Hit”. Skiftet i känsla påverkar hur jag tar mig an spelet. Min största frustration i spelet kom när jag behövde samla ihop pengar för att föra berättelsen framåt, men förlorade gång på gång i Lucky Hit. Jag avskyr slumpen och det är det enda det spelet går ut på.\n\n![Shenmue I & II](https://gamingbolt.com/wp-content/uploads/2018/05/shenmue.jpg)\n\nBerättelsen i Shenmue 2 är mer varierad och har längre interaktioner med många av spelets karaktärer. En av de första återkommande karaktärerna i berättelsen är Joy, en gängmedlem som alltid kommer in på sin motorcykel för att rädda Ryo från fara. Hon har mer djup än de flesta karaktärerna i första spelet. I Hong Kong måste Ryo lära sig vad som krävs för att bli en mästare i Kung Fu. Det skapar en konflikt med Ryos hämndtankar och det är något som ofta tas upp av hans Mentor Xiuying Hong. Själva kärnan i berättelsen är dock samma som i första spelet och interaktionen med stadens invånare är fortfarande det primära sättet att föra berättelsen framåt. \n\nDenna gången är dock samtalen med invånarna inte enbart begränsat till att samla information för att komma närmare Lan Di, utan det går även att fråga dem om jobb, gambling och var man kan hitta de olika pantbankerna i staden. Det här är en aspekt som hjälper till när man verkligen behöver pengar och det finns några tillfällen då man måste samla ihop en viss mängd Hong Kong dollar för att kunna komma vidare. \n\nTill skillnad från de få spel som ändå försökt efterlikna delar av Shenmue så är striderna verkligen inte en central del av spelet. För mig är det otroligt konstigt att spelet har ett avancerat stridssystem när det knappt används i varken det första spelet eller det andra. Det känns lite som att den aspekten inte helt passar in i resten av upplägget. Striderna är ju helt klart välkomnande för de ger spelet mer variation, men de är också som bäst okej. Inget jag kommer tänka på när jag tänker på Shenmue.\n\n\nDet engelska röstskådespeleriet känns stelt och saknar inlevelse, vilket i sin tur gör att de emotionella tonerna i spelet blir smått komiska istället. Karaktärernas interaktioner låter inte trovärdiga och påminner mig lite om Gösta Ekmans inlevelse i dokumentärfilmen Pingvinresan. Det är skönt att det går byta från engelska till japanska. För mig blir det mycket mer trovärdigt med ursprungsspråket och det blir också en mer emotionell resa. De två olika språkvalen ger helt enkelt två skilda upplevelser av en och samma berättelse. \n\nMusiken är otroligt välkomponerad och förmedlar det visuella och det tematiska väl. Den ger liv till staden, naturen, kulturen, spelets karaktärer och förstärker händelserna i berättelsen. Det finns även en bra dynamik mellan olika stilar och ljudbilder. Jag älskar min första interaktion med mataffären i Dobuita. Deras jingel kan vara en av de gladaste jag hört och det fick mig att må bra. Spelets musik klättrar högt upp på min lista över den bästa musiken i spel. \n\nDet är uppenbart att Shenmue 1 och 2 planerades som ett enda stort spel, men att det inte gick att få ihop i tid och det är skönt att kunna ta del av båda i ett och samma paket. De flyter ihop med varandra så bra. \n\nShenmue 1 och 2 var helt klart unika och ambitiösa projekt för sin tid. Det spelen lyckades åstadkomma känner jag inte riktigt att något annat spel eller spelserie lyckats med än idag. De är långt ifrån perfekta, men de erbjuder en bredd på spelmarknaden som jag uppskattar. Berättelsen, musiken och den visuella stilen tycker jag håller än idag, medan andra aspekter, såsom styrningen, striderna och röstskådespeleriet inte håller en lika hög standard. Det är här jag hoppas Yu Suzuki förändrar med uppföljaren. För mig är Shenmue-spelen underbara och en nostalgitripp tillbaka till en era av spel som inte riktigt tillverkas idag, men jag förstår också att spelen inte är för alla. Det här är första gången jag spelar den här spelserien och det här paketet fick mig att bli väldigt nyfiken på att se Yu Suzuki få avsluta sin skapelse.\n\n",
                    "category": "games",
                    "coverImage": "http://images.pushsquare.com/news/2018/04/soapbox_why_you_should_play_shenmue_i_and_ii_on_ps4/attachment/0/original.jpg",
                    "postType": "review",
                    "createdAt": "2018-10-05T15:27:14.276Z",
                    "updatedAt": "2018-10-06T00:16:11.065Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 15,
                    "latestReply": "2018-10-06T00:16:11.062Z",
                    "latestReplyUserId": "5bb7fdfb8fef22001d902d55",
                },
            ],
            "users": [
                {
                    "id": "5bb9ef7d1f1848001d97f2e6",
                    "name": "andreaslennarts",
                    "role": "user",
                    "createdAt": "2018-10-07T11:35:25.245Z",
                    "status": "active",
                },
                {
                    "id": "5bb89a1b8fef22001d90302c",
                    "name": "Anubis",
                    "role": "user",
                    "createdAt": "2018-10-06T11:18:51.184Z",
                    "status": "active",
                },
                {
                    "id": "5bb86bda8fef22001d902ea2",
                    "name": "Nikeplektrum",
                    "role": "user",
                    "createdAt": "2018-10-06T08:01:30.658Z",
                    "status": "active",
                },
                {
                    "id": "5bb7fdfb8fef22001d902d55",
                    "name": "Piccolo",
                    "picture": "9391ac81-beae-478d-b508-acfc479bc607.jpg",
                    "role": "user",
                    "createdAt": "2018-10-06T00:12:43.008Z",
                    "status": "active",
                },
                {
                    "id": "5bb7fa1b8fef22001d902d40",
                    "name": "Harjaren",
                    "role": "user",
                    "createdAt": "2018-10-05T23:56:11.704Z",
                    "status": "active",
                },
                {
                    "id": "5bb7e8478fef22001d902cd5",
                    "name": "Tenkai Star",
                    "picture": "ede40901-2c52-4e59-81de-98c1975ab9dd.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T22:40:07.648Z",
                    "status": "active",
                },
                {
                    "id": "5bb7de268fef22001d902c83",
                    "name": "Svea",
                    "role": "user",
                    "createdAt": "2018-10-05T21:56:54.513Z",
                    "status": "active",
                },
                {
                    "id": "5bb7d5f68fef22001d902c01",
                    "name": "Det lilla svinet",
                    "picture": "46447bbf-df49-4c9f-aa5d-63b12f840afc.png",
                    "role": "user",
                    "createdAt": "2018-10-05T21:21:58.341Z",
                    "status": "active",
                },
                {
                    "id": "5bb7d4628fef22001d902be9",
                    "name": "Schultz",
                    "picture": "9492680e-15f7-4849-95c3-6c90b3bf7e2a.png",
                    "role": "user",
                    "createdAt": "2018-10-05T21:15:14.292Z",
                    "status": "active",
                },
                {
                    "id": "5bb7cd3a8fef22001d902b61",
                    "name": "Delacroix",
                    "role": "user",
                    "createdAt": "2018-10-05T20:44:42.285Z",
                    "status": "active",
                },
                {
                    "id": "5bb7b5768fef22001d9028ea",
                    "name": "kavakava",
                    "picture": "cccf1061-f805-4081-9022-116d201a7260.png",
                    "role": "user",
                    "createdAt": "2018-10-05T19:03:18.943Z",
                    "status": "active",
                },
                {
                    "id": "5bb7af638fef22001d9027a4",
                    "name": "mazerfaka",
                    "picture": "0b80e031-2fb1-4e03-899c-f0dabfdba94c.png",
                    "role": "user",
                    "createdAt": "2018-10-05T18:37:23.377Z",
                    "status": "active",
                },
                {
                    "id": "5bb7af388fef22001d90279a",
                    "name": "Coola Anton i Fräcka Bergen",
                    "picture": "33dc8197-1471-43a5-b28e-4eb8349e1ca3.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:36:40.235Z",
                    "status": "active",
                },
                {
                    "id": "5bb7ad278fef22001d902723",
                    "name": "Benedict",
                    "role": "user",
                    "createdAt": "2018-10-05T18:27:51.534Z",
                    "status": "active",
                },
                {
                    "id": "5bb7ac428fef22001d9026ea",
                    "name": "Raderad",
                    "role": "user",
                    "createdAt": "2018-10-05T18:24:02.802Z",
                    "status": "active",
                },
                {
                    "id": "5bb7abbb8fef22001d9026c9",
                    "name": "ppr74",
                    "role": "user",
                    "createdAt": "2018-10-05T18:21:47.597Z",
                    "status": "active",
                },
                {
                    "id": "5bb7aa868fef22001d902665",
                    "name": "Kiki",
                    "picture": "8b0e6e55-6b4a-4386-8551-e510b5e62fd4.png",
                    "role": "user",
                    "createdAt": "2018-10-05T18:16:38.350Z",
                    "status": "active",
                },
                {
                    "id": "5bb7a9cc8fef22001d9025ef",
                    "name": "Terzom",
                    "picture": "e2c5ed0c-1568-4ab9-bfe4-77e2553d148c.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:13:32.839Z",
                    "status": "active",
                },
                {
                    "id": "5bb77830066d1b001d528a1c",
                    "name": "Elin Ekberg",
                    "picture": "a97bf0c2-4de3-4888-8acc-78f9b58e65dc.png",
                    "role": "user",
                    "createdAt": "2018-10-05T14:41:52.609Z",
                    "status": "active",
                },
                {
                    "id": "5bb773d1066d1b001d528a17",
                    "name": "Simon Liljedahl",
                    "picture": "5cff7bc0-68b3-47c8-90a7-dd1d20f3885d.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T14:23:13.767Z",
                    "status": "active",
                },
                {
                    "id": "5bb76b06066d1b001d528a04",
                    "name": "Petter Arbman",
                    "picture": "6576d9be-119f-448c-aa06-c330a54e4e0a.jpg",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:45:42.886Z",
                    "status": "active",
                },
                {
                    "id": "5bb75ec2066d1b001d5289e9",
                    "name": "Aaron Vesterberg Ringhög",
                    "picture": "b44e7341-421f-48fb-81fc-331acd93ba34.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T12:53:22.371Z",
                    "status": "active",
                },
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_games(page=91)

        self.assertDictEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_games_failure_page_too_low(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too low",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_games(page=-1)

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_games_failure_page_too_high(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too high",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"posts": [], "users": []}
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_games(page=999)

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_other_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bc22315c0c2ba001d07b888",
                    "title": "Tipsa om Youtube-kanaler som är värda att följa (och varför!)",
                    "body": "Jag har några nödvändiga stopp på Youtube.\n\nDit jag alltid går när det finns en ny film.\n\nDet är dom här:\n\n**Good Mythical Morning**\nhttps://www.youtube.com/channel/UC4PooiX37Pld1T8J5SYT-SQ\nGMM har ett nytt avsnitt varje dag klockan 12:00 (och ett extra i Good Mythical More). Det här är (om du på något sätt missat Rhett & Link) en talkshow i miniformat, med fokus på olika tester.\n\n**Ashens**\nhttps://www.youtube.com/channel/UCxt9Pvye-9x_AIcb1UtmF1Q\nDet här är för alla er som tycker att Amiga Power hade världens bästa humor.\n\n**You suck at cooking**\nhttps://www.youtube.com/channel/UCekQr9znsk2vWxBo3YiLq2w\nDet är sällan något nytt händer på YSAC, men när det händer är det alltid det bästa som hänt just den veckan.\n\n**Juns Kitchen**\nhttps://www.youtube.com/channel/UCRxAgfYexGLlu1WHGIMUDqw\nMer mat, men så långt från YSAC på matspektrumet som det går att komma. Det här är imponerande mat som du aldrig kommer att göra lika bra själv och världens mest väluppfostrade katter. \n\n**The Report of the Week**\nhttps://www.youtube.com/channel/UCeR0n8d3ShTn_yrMhpwyE1Q\nSnabbmatsrecensioner med en så torr humor att den måste ha kostym. Det är så här jag föreställer mig  att Alexander Rehnman skulle vara, om han recenserade snabbmat.\n\n**The Try Guys**\nhttps://www.youtube.com/channel/UCpi8TJfiA4lKGkaXs__YdBA\nPå något sätt lyckades The Try Guys lämna Buzzfeed OCH ta med sig varumärket. Zach är naturligtvis bäst.\n\n**Challa**\nhttps://www.youtube.com/channel/UCQa2X1CNCxWF3M6h68g5q6g\nTecknare med humor och självdistans. Och med ett väldigt speciellt sätt att artikulera sig som jag finner fascinerade att lyssna på.\n\n**Worth it**\nhttps://www.youtube.com/playlist?list=PL5vtqDuUM1DmXwYYAQcyUwtcalp_SesZD\nEn serie under Buzzfeed där Steven och Andrew testar tre versioner av samma maträtt, men i tre helt olika prisklasser.\n\nNu är det din tur - vad följer du?\n\n\n",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-13T16:53:41.038Z",
                    "updatedAt": "2018-10-15T10:17:00.297Z",
                    "userId": "5bb76074066d1b001d5289ed",
                    "replies": 26,
                    "latestReply": "2018-10-15T10:17:00.291Z",
                    "latestReplyUserId": "5bb76b06066d1b001d528a04",
                },
                {
                    "id": "5bbcb23d2e1d32001d523816",
                    "title": "Tack Loading",
                    "body": '# UPPDATERING\n\n## Kära Loadingvänner! \n\n\nVi vill först börja med att tacka er för en fantastisk lanseringshelg. Den fantastiskt trevliga och positiva stämning som rått och hur pass väl allt har fungerat, spartanskt utförande till trots, värmer våra hjärtan. \n\n\nEr feedback är otroligt värdefull. Just nu ligger störst fokus vid att, i den takt det är möjligt för vår hjälte Stanislav Izotov, rätta till diverse frågetecken och se till att den grundläggande upplevelsen blir så smidig som möjligt. På lång sikt kommer ni att vara en del av hur vårt community utformas.\n\n\n**Vi vill ta detta tillfälle i akt att förklara varför vi valde att lansera nya Loading i ett så ofärdigt skick.**\n\n\nDet handlar om två saker:\n\n\nDet viktigaste är för att vi vill att ni ska känna att ni har möjlighet att direkt påverka utvecklingen och känna er som en del av hela upplevelsen. Att innerst inne veta att alla ni som kommenterat kring saker också sett till att de har blivit till verklighet. Det gäller även er som stöttar oss via Patreon, vilket visar att ni vill se att vi lyckas. Det ger oss en möjlighet att skapa den mötesplats och arena vi vill tillsammans med er, även om ni inte uttrycker det i text.\n\n\nDet andra är för att vi som jobbat med detta projekt i runt fyra månader nu och behövde en milstolpe för att fortsätta sträva framåt, hitta ny energi och motivation - att helt enkelt få en bekräftelse på att det var möjligt och att ni fortfarande var med oss!\n\n\nTill sist vill vi också lägga vikt vid att nämna att ni inte ska känna er oroliga för att era inlägg ska stryka på foten när sidan genomgår sin metamorfos längs vägen. Trots att sidan är som den är och att rätt stora förändringar kommer att ske, kommer alla era inlägg finnas kvar tack vare den molnbaserade serverlösning vi har valt att använda. Det går knappt beskriva skillnaden att bygga en sådan här tjänst idag jämfört med hur det var för 10-20 år sedan.\n\n\n![alt text](https://i.imgur.com/zSHYABw.png"pixelhjärta.jpg")\n\n\n__Redaktionen__',
                    "category": "other",
                    "coverImage": "https://i.imgur.com/Ycrx9Ci.jpg",
                    "postType": "update",
                    "createdAt": "2018-10-09T13:50:53.896Z",
                    "updatedAt": "2018-10-14T04:36:51.558Z",
                    "userId": "5bb751cb066d1b001d5289e0",
                    "replies": 12,
                    "latestReply": "2018-10-14T04:36:51.556Z",
                    "latestReplyUserId": "5bb7ab038fef22001d902690",
                },
                {
                    "id": "5bbfbbe57f24bc001d2b6693",
                    "title": "Hyrenbostad.se, Trovit etc.",
                    "body": 'Jag har inte stått i bostadskö speciellt länge tyvärr, men jag samlar pengar fort och förväntas kunna köpa något väldigt fint i slutet på nästa sommar.\nSom Stockholmare får man oftast stå i kö i 10-15år för att hitta något ordentligt, speciellt i innerstaden. Eller så kan man köpa loss en liten 1a/2a för ca 2miljoner.\nMen jag råkade precis klicka in på sidor där folk hyr ut sina lägenheter för en svinliten avgift (priset för 2 nätter på hotell ungefär) och låter en bo där under en "obegränsad" period.\nVilket är sjukt.\n\nNågon som vet om det rör sig om helt fejkade sidor, eller har någon här någon som helst erfarenhet? För jag är väldigt förvirrad över situationen, vad är det jag missat? Alla som står utan bostad hade ju klickat hem dessa bostäder på 5 sekunder?\n\nHär är ett exempel. Innerstan, en 2:a, 2.300kr i månaden, obegränsad uthyrning.\nhttps://www.hyrenbostad.se/hyresbostad/678999/2-rums-laegenhet-paa-39-m?utm_campaign=Premium&utm_source=Trovit&utm_medium=CPC',
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-11T21:08:53.826Z",
                    "updatedAt": "2018-10-12T09:39:14.810Z",
                    "userId": "5bbbe77bf1deda001d33bde2",
                    "replies": 4,
                    "latestReply": "2018-10-12T09:39:14.807Z",
                    "latestReplyUserId": "5bb75fb7066d1b001d5289eb",
                },
                {
                    "id": "5bbf7e767f24bc001d2b651d",
                    "title": "Glass (M. Night Shyamalan) - Trailer 2",
                    "body": "Uppföljaren till Unbreakable och Split.\n\nPremiär i början av nästa år.\n\nhttps://www.youtube.com/watch?v=Q7ztHi9ejp4",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-11T16:46:46.357Z",
                    "updatedAt": "2018-10-12T04:51:56.215Z",
                    "userId": "5bb76074066d1b001d5289ed",
                    "replies": 3,
                    "latestReply": "2018-10-12T04:51:56.213Z",
                    "latestReplyUserId": "5bb773d1066d1b001d528a17",
                },
                {
                    "id": "5bbef4c87f24bc001d2b627d",
                    "title": "Den stora AI tråden",
                    "body": "Vad har ni för tankar kring ämnet?  \n\nTror ni alls att en maskin kan uppvisa vad som vi menar är intelligens? \n\nMedvetande? \n\nLiv? \n\nNi fattar. \n\nSjälv kommer jag stå först i robotarnas befrielsefront!",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-11T06:59:20.846Z",
                    "updatedAt": "2018-10-11T09:24:58.768Z",
                    "userId": "5bb7b6c48fef22001d90292c",
                    "replies": 3,
                    "latestReply": "2018-10-11T09:24:58.761Z",
                    "latestReplyUserId": "5bb7b6c48fef22001d90292c",
                },
                {
                    "id": "5bbb7886f1deda001d33bb9c",
                    "title": "Problem med att logga in/Skapa konto",
                    "body": "Jag tänkte bara tipsa er som har problem med att logga in eller problem med att skapa konto att det verkar som att rensa historiken med cachen och allt löser det problemet. Iallafall på chrome webbläsaren. (:",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-08T15:32:22.920Z",
                    "updatedAt": "2018-10-11T04:40:16.482Z",
                    "userId": "5bb7a9ea8fef22001d9025ff",
                    "replies": 4,
                    "latestReply": "2018-10-11T04:40:16.477Z",
                    "latestReplyUserId": "5bbed3bd7f24bc001d2b6221",
                },
                {
                    "id": "5bbe2ac5524a40001d207584",
                    "title": "Orkanen Michael och Florida",
                    "body": "Orkanen Michael närmar sig Florida.\n\nDen är nästan där.\n\nDen senaste mätningen har satt orkanen till en kategori 4, men den är nära fem och kommer bli starkare hela vägen in till land. Det är med stor sannolikhet den mest intensiva storm som träffat Florida sedan man började mätningarna (för länge sedan).\n\nDet är en knapp timme kvar innan Michael når land.\n\nDet går att hitta livesändningar från dom som jagar stormar här:\n\nhttps://livestormchasing.com/map",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-10T16:37:25.976Z",
                    "updatedAt": "2018-10-10T18:21:17.800Z",
                    "userId": "5bb76074066d1b001d5289ed",
                    "replies": 4,
                    "latestReply": "2018-10-10T18:21:17.798Z",
                    "latestReplyUserId": "5bb76074066d1b001d5289ed",
                },
                {
                    "id": "5bb78aba066d1b001d528a30",
                    "title": "Hur funkar nya Loading a.k.a Loading for dummies",
                    "body": "Nya Loading ser lite annorlunda som du kanske har märkt =) på framsidan kommer du hitta olika kategorier som vi kommer att använda för olika sorters material och för olika syften:\n\n* UPPDATERING\n\n    Kategorin vi kommer att använda då vi annonserar uppdateringar, händelser eller nyheter\n* ÅSIKT\n\n    Här kommer vi lägga våra krönikor, förtittar, reportage och intervjuer e.t.c\n* SAMTAL\n\n    Här kommer vi lyfta intressanta och spännande trådar från forumet som vi tycker förtjänar lite extra uppmärksamhet och kärlek\n* RECENSION\n\n    ̣Vi kommer såklart fortsätta skriva recensioner antingen av spel vi fått från utgivare eller som vi köpt själva.\n* PODCAST\n\n    I Loadings podcastnätverk ingår TV-spelspodden och Spelsnack. Här kan ni ta del av några av Loadingredaktionens tankar kring spel och spelindustrin.\n* STREAM\n\n    Vi kommer fortsätta att streama när vi spelar spel via våra streamingkanaler som du kan hitta längst ner på sidan.\n\n**Forumet**\nSom du snabbt kommer att märka har vi bara två forumkategorier på nya Loading. Det är SPEL-forumet och ANNAT-forumet - Vi vill helt enkelt att så många som möjligt ska delta i de samtal som förs och att det som är mest aktuellt kommer att vara det som flest vill vara en del av.\n\n**Att Använda Loading på mobilen**\nVi har märkt att olika webbläsare och mobiler hanterar nya Loading lite olika. Ett tips är att välja att visa sidan i datoranpassat läge eller liknande funktion som du hittar i inställningarna. I övrigt är nya Loading skapat för att fungera lika bra på mobilen som på datorn.\n\n**Publicera inlägg:**\nFör att publicera ett inlägg skriver du i rutan som vanligt trycker på “skicka” så är det klart!\n\nVill du snygga till ditt inlägg så kan vi berätta att nya Loading använder Markdown som verktyg för att formatera text. Det är ett jättesmidigt verktyg och du kan hitta en jättebra lathund [**HÄR**](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)\noch vill du testa och se hur ditt inlägg ser ut innan du publicerar det kan du göra det [**HÄR**](https://dillinger.io)\n\nVälkommen!",
                    "category": "other",
                    "postType": "regular",
                    "createdAt": "2018-10-05T16:00:58.973Z",
                    "updatedAt": "2018-10-07T16:57:29.528Z",
                    "userId": "5bb7618d066d1b001d5289ef",
                    "replies": 33,
                    "latestReply": "2018-10-07T16:57:29.526Z",
                    "latestReplyUserId": "5bb7618d066d1b001d5289ef",
                },
            ],
            "users": [
                {
                    "id": "5bbed3bd7f24bc001d2b6221",
                    "name": "voldo83#912",
                    "picture": "ddd472f8-7a19-456c-8321-a59921afe9e8.jpg",
                    "role": "user",
                    "createdAt": "2018-10-11T04:38:21.270Z",
                    "status": "active",
                },
                {
                    "id": "5bbbe77bf1deda001d33bde2",
                    "name": "VodkaCitron",
                    "picture": "50836acb-0f85-4876-9bf6-c895dec4eaed.png",
                    "role": "user",
                    "createdAt": "2018-10-08T23:25:47.618Z",
                    "status": "active",
                },
                {
                    "id": "5bb7b6c48fef22001d90292c",
                    "name": "nmhbm",
                    "picture": "9306e0da-fa8f-4d40-87b5-aeb3066c0ccb.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T19:08:52.800Z",
                    "status": "active",
                },
                {
                    "id": "5bb7ab038fef22001d902690",
                    "name": "Metatron",
                    "picture": "c10b245d-56b3-4f2b-b165-eec55a38b3ec.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:18:43.176Z",
                    "status": "active",
                },
                {
                    "id": "5bb7a9ea8fef22001d9025ff",
                    "name": "Eric",
                    "picture": "38a95df8-b19e-4e57-9e09-28704fb53b5f.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:14:02.248Z",
                    "status": "active",
                },
                {
                    "id": "5bb773d1066d1b001d528a17",
                    "name": "Simon Liljedahl",
                    "picture": "5cff7bc0-68b3-47c8-90a7-dd1d20f3885d.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T14:23:13.767Z",
                    "status": "active",
                },
                {
                    "id": "5bb76b06066d1b001d528a04",
                    "name": "Petter Arbman",
                    "picture": "6576d9be-119f-448c-aa06-c330a54e4e0a.jpg",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:45:42.886Z",
                    "status": "active",
                },
                {
                    "id": "5bb7618d066d1b001d5289ef",
                    "name": "Niklas Karlsson",
                    "picture": "c8f27420-089e-4f9a-adf9-8b7c9fb85d4a.png",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:05:17.573Z",
                    "status": "active",
                },
                {
                    "id": "5bb76074066d1b001d5289ed",
                    "name": "Oskar Skog",
                    "picture": "4c5f014d-2266-4642-bc20-5edff5ac33a9.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T13:00:36.127Z",
                    "status": "active",
                },
                {
                    "id": "5bb75fb7066d1b001d5289eb",
                    "name": "Johan Lorentzon",
                    "picture": "0b0bcb70-54c3-4b7d-9238-ac7a08b8fb64.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T12:57:27.746Z",
                    "status": "active",
                },
                {
                    "id": "5bb751cb066d1b001d5289e0",
                    "name": "Isabell Rydén",
                    "picture": "b12a2fe1-101e-4ee3-9679-941b24b02e20.jpg",
                    "role": "editor",
                    "createdAt": "2018-10-05T11:58:03.230Z",
                    "status": "active",
                },
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_games(page=91)

        self.assertDictEqual(response.get("data"), expected_response)

        threads = response.get("data").get("posts")

        for thread in threads:
            self.assertEqual(thread.get("category"), "other")

    @patch("loading_sdk.api.requests")
    def test_get_other_failure_page_too_low(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too low",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_other(page=-1)

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_other_failure_page_too_high(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too high",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"posts": [], "users": []}
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_other(page=999)

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_editorials_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bb797b8066d1b001d528a43",
                    "title": "Bli en del av vår Patreon",
                    "body": "![Patreon](https://i.imgur.com/lNDGvZd.jpg)\n\n### UPPDATERING 20181208:\n\nHej alla ni tappra underbara Loadare som bidrar till driften, utvecklingen och det redaktionella bakom forumet. Vi vet att vi har varit dåliga på att uppdatera vår Patreon, men det kommer!\nStort tack för alla bidrag och STORT TACK för att ni är ni är så fina som ni är! <3\n\n### ORIGINALPOST:\n\n### Kära Loadare.\n\nFör vissa av oss har Loading alltid varit som ett andra hem. En plats som är något större än enbart ett forum på internet.\n\nKanske är du en av oss?\n\nIdag drivs Loading ideellt av en fristående grupp eldsjälar som behöver din hjälp för att täcka kostnader för underhåll och drift. Med lite från många kan vi lyckas att hålla liv i forumet samt utveckla och bygga ut det allt eftersom.\nVi tror och hoppas att du som användare uppskattar forumet och det som redaktionen skapar för dig.\n\nVi har uppskattat att det kommer kosta oss ungefär 1000 kr varje månad för underhåll och drift av sidan, vilket vi anser är den absolut viktigaste bakgrunden till varför vi upprättar en Patreon. Skulle vi få in mer pengar än det absolut nödvändigaste ser vi detta som en investering i de resurser som krävs för vidareutveckling av funktioner på Loading. Utöver det har vi även satt ett mål för att kunna erbjuda redaktionellt material av större kvalité.\n\nVarma hälsningar och tack på förhand för din tid.\n\nhttps://www.patreon.com/loadingse/overview\n\n/Loading-redaktionen\n",
                    "category": "other",
                    "coverImage": "https://i.imgur.com/lNDGvZd.jpg",
                    "postType": "update",
                    "createdAt": "2018-10-05T16:56:24.766Z",
                    "updatedAt": "2018-12-09T09:07:22.386Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 36,
                    "edits": 1,
                    "lastEdit": "2018-12-08T16:26:36.325Z",
                    "latestReply": "2018-12-09T09:07:22.382Z",
                    "latestReplyUserId": "5bb7e4ab8fef22001d902cb9",
                },
                {
                    "id": "6020fd086544a9001ed1688c",
                    "title": "Ekonomisk rapport för 2020 ",
                    "body": "![](https://i.imgur.com/Dr8kWZy.png)\n\n2020 var ett omtumlande år för världen, och ett spännande år för Loading. Under året som gått har vi inte bara sett mängder av recensioner och spännande trådar och diskussioner passera förbi, utan forumet har också fått sig ett ordentligt lyft. Utöver en visuell makeover har vårt skickliga utvecklingsteam levererat efterlängtade funktioner som citering, mörkt läge, ordentliga moderatorverktyg och inbäddning av YouTube-klipp, samt en och annan buggfix och andra trevliga grejer under huven. Loading kommer så klart fortsätta utvecklas under 2021 också.\n\nEftersom vi inte skulle kunna göra det vi gör [utan ert ekonomiska stöd](https://www.patreon.com/loadingse) vill vi tala om exakt vad era pengar går till.\n\nUnder 2020 hade Loading intäkter på **20 978,08 kr**, fördelade så här:\n\n* **Patreon-inkomster:** 18 571,47 kr\n* **Återbetalning av oavsiktligt hamburgarköp:** 82 kr (mer om detta nedan)\n* **Kvarglömda Patreon-pengar från innan vi skaffade eget bankkonto:** 2 324,61 kr\n\nVåra utgifter uppgick till **13 704,20 kr:**\n* **Driftskostnader (serverhyra och dylikt):** 10 281, 20 kr\n* **Bankavgifter:** 1 100 kr\n* **Oavsiktligt hamburgarköp: (en hungrig redaktionsmedlem blippade fel kort i kassan):** 82 kr\n* **Inköp av kuvert och frimärken att posta papper som ska skrivas på med:** 190 kr\n* **Spelinköp till recensioner:** 2 051 kr\n\nSpelinköpen var följande:\n* **Nioh 2:** 699 kr\n* **What the Golf:** 156 kr\n* **The Last of Us Part II:** 699 kr\n* **Cyberpunk 2077:** 497 kr\n\nDetta resulterade i att vi gick **7 273,88 kr plus.** Eftersom Loading drivs ideellt har vi inga planer på att de här pengarna ska stoppas i redaktionens fickor eller liknande, utan de ska investeras i att fortsätta driva Loading på olika sätt, till exempel genom inköp av spel vi inte får recensionsexemplar av, eller inköp av tjänster som underlättar utveckling eller drift av sidan. (Med detta menas då mjukvarutjänster, då vi tyvärr inte har råd att hyra in professionella utvecklare och betala skälig ersättning till dem.) En del av pengarna kommer också användas för att bygga upp en buffert i händelse av oförutsedda utgifter.\n\nNu blickar vi framåt mot resten av 2021, som förhoppningsvis kommer bli ännu ett fantastiskt år för Loading. Ett forum är ingenting utan sina användare, så vi tackar så hjärtligt för att ni finns här och stöttar oss.\n\nDet är ni som sporrar oss att kämpa ända in i kaklet för att göra Loading till den bästa community det kan vara.\n\nNi är anledningen att det överhuvudtaget finns ett Loading.\n\nÄn en gång, tack.\n\nVänliga hälsningar,\nLoadingredaktionen\n\n![](https://i.imgur.com/6zl9mey.png)\n",
                    "category": "games",
                    "coverImage": "https://i.imgur.com/Dr8kWZy.png",
                    "postType": "update",
                    "createdAt": "2021-02-08T08:57:44.724Z",
                    "updatedAt": "2021-02-09T08:58:38.826Z",
                    "userId": "5bbd0e7403dc9d001d9a5565",
                    "replies": 26,
                    "edits": 2,
                    "lastEdit": "2021-02-08T13:03:40.525Z",
                    "latestReply": "2021-02-09T08:58:38.826Z",
                    "latestReplyUserId": "5bb751cb066d1b001d5289e0",
                },
                {
                    "id": "61af0e4c38bbee001f35d5da",
                    "title": "Loadingbössan 2021 – Loading stödjer Musikhjälpen",
                    "body": "![](https://i.imgur.com/l7xD1oT.png)\n\n# LOADINGBÖSSAN 2021\n\nGivmildhetens högtid är kommen - Julen. Sedan 2008 är [Musikhjälpen](https://sverigesradio.se/artikel/om-musikhjalpen) mer eller mindre befäst som en riktig jultradition. Genom åren har totalt ungefär 425 miljoner kronor skänkts till diverse välgörande ändamål.\n\nDet är Norrköping som står värd för Musikhjälpen 2021 och årets tema är: **För en värld utan barnarbete.** För första gången på 20 år har man sett att förekomsten av barnarbete har ökat. Mer information om temat kan du läsa på [Sveriges Radios webbplats](https://sverigesradio.se/artikel/for-en-varld-utan-barnarbete).\n\nSom tidigare år har vi självklart fixat en [**Loadingbössa**](https://bossan.musikhjalpen.se/loadingboessan-2021) för dig som vill bidra i Loadings namn. Förra året blev Loadingbössan fylld med 550kr. Det bör vi väl kunna bräcka?\n\n![](https://i.imgur.com/6zl9mey.png)\n",
                    "category": "games",
                    "coverImage": "50f88615-b5b5-473c-8b86-bba25cf1604f.png",
                    "postType": "update",
                    "createdAt": "2021-12-07T07:33:32.758Z",
                    "updatedAt": "2021-12-30T11:56:58.590Z",
                    "userId": "5bbd0e7403dc9d001d9a5565",
                    "replies": 23,
                    "latestReply": "2021-12-30T11:56:58.589Z",
                    "latestReplyUserId": "5bb7618d066d1b001d5289ef",
                },
                {
                    "id": "5c2b3939f425c2001d0d47b2",
                    "title": "Loadings Patreon",
                    "body": "![](https://i.imgur.com/312v4k9.png)\n# Tack för en bra (ny)start!\n\nHej Loading!\n\nHär kommer en uppdatering kring [vår Patreon](https://www.patreon.com/loadingse) och en visning på hur ert ekonomiska stöd just nu förvaltas:\n\nInkomster hittills via vår Patreon (*betalas ut i mitten av efterkommande månad*) uppgår till totalt **5 288,95 kr**.\n* 13 november: **2 879,70 kr**\n* 14 december: **2 409,25 kr**\n\nUtgifter hittills uppgår till totalt **3 369 kr**:\n* Övertagande av domänen från Reset Media: **950 kr**\n   (*detta är en kostnad som webbhotellet tog ut*)\n* Kostnad för databas i oktober: **641,56 kr**\n* Kostnad för domän i oktober: **55,61 kr**\n* Kostnad för databas i november: **717,24 kr**\n* Kostnad för domän i november: **19,74 kr**\n* Darksiders 3 för recension: **549 kr**\n   (*ingen recensionskod från utgivaren*)\n* Katamary Damacy Reroll för recension: **179 kr**\n   (*slut på recensionskoder hos utgivaren*)\n\nSom ni ser har vi ett överskott i vår kassa. Överskottet kommer att förvaltas av redaktionen för behov vid redaktionellt material samt fortsatt buffert för driften av Loading. \n\nIdag drivs Loading av eldsjälar från både redaktionen och forumet. Inga pengar kommer att gå till någon form av lön. Vad vi däremot kommer att titta på är scenarion där vi kan beställa ett jobb från en extern part som hjälper till med vidareutvecklingen av sidan.\n\nTills vidare fortsätter Stanislav att arbeta på sidan tillsammans med Terzom, som ni säkert också känner igen från forumet. \n\nHär är en kort redovisning över vad som gjorts sedan vi lanserade i oktober:\n* Tagit fram textredigerare med möjlighet att redigera sitt inlägg med Markdown.\n* Möjlighet att redigera ett redan skapat inlägg.\n* Uppdaterad styling på inlägg.\n* Möjlighet att ha sin egen profilbild.\n* Pågående arbete med olika kontoflöden (*registrering, avregistrering, lösenordsändring med mera*) \n* Justeringar för mobil ökad läsbarhet på mobil plattform.\n* Allmänna buggfixar och förfiningar.\n\nEn del av vår vision är att ni på Loading ska ha möjligheten att påverka sidans innehåll. Därför undrar vi om ni vill vara med och ge förslag på vilka spel vi ska köpa och recensera?\n\nVi vill också passa på att säga att vi uppskattar all er feedback som ni har gett oss i [förslagstråden] (https://loading.se/post/5bb790e5066d1b001d528a3a), och vi vill också att ni medlemmar fortsätter att komma med förslag på vad som kan förbättras och vad för innehåll ni vill se mer av. \n\nOch du, tack för ditt stöd, Loading är inget utan dig!\n\nFölj med oss till 2019!\n\nMed varma hälsningar,\nRedaktionen\n\n![](https://i.imgur.com/RE2YtkV.png)\n\n",
                    "category": "other",
                    "coverImage": "https://i.imgur.com/312v4k9.png",
                    "postType": "update",
                    "createdAt": "2019-01-01T09:56:09.736Z",
                    "updatedAt": "2019-02-05T15:47:45.016Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 15,
                    "edits": 4,
                    "lastEdit": "2019-01-01T10:30:11.112Z",
                    "latestReply": "2019-02-05T15:47:45.009Z",
                    "latestReplyUserId": "5bb7b1ac8fef22001d902820",
                },
                {
                    "id": "6038bf69e7b0bb001e6246e1",
                    "title": "Loadings Patreon",
                    "body": "![](https://i.imgur.com/QQWY9dI.png)\n\nKära Loadare.\nFör vissa av oss har Loading alltid varit som ett andra hem. En plats som är något större än enbart ett forum på internet.\n\nIdag drivs Loading ideellt av en fristående grupp eldsjälar som behöver din hjälp för att täcka kostnader för underhåll och drift. Med lite från många kan vi lyckas att hålla liv i forumet samt utveckla och bygga ut det allt eftersom.\nVi tror och hoppas att du som användare uppskattar forumet och det som redaktionen skapar för dig.\n\nVi har uppskattat att det kommer kosta oss ungefär 1000 kr varje månad för underhåll och drift av sidan, vilket vi anser är den absolut viktigaste bakgrunden till varför vi upprättat en Patreon. Skulle vi få in mer pengar än det absolut nödvändigaste ser vi detta som en investering i Loadings framtid, till exempel genom inköp av tjänster och material som låter oss förbättra sidan och det redaktionella innehållet.\n\nVarma hälsningar och tack på förhand för din tid och ditt stöd.\n\nhttps://www.patreon.com/loadingse/overview\n\n/Loading-redaktionen\n\n![](https://i.imgur.com/6zl9mey.png)\n",
                    "category": "other",
                    "coverImage": "https://i.imgur.com/QQWY9dI.png",
                    "postType": "update",
                    "createdAt": "2021-02-26T09:29:13.405Z",
                    "updatedAt": "2021-02-26T10:07:50.843Z",
                    "userId": "5bbd0e7403dc9d001d9a5565",
                    "replies": 2,
                    "edits": 1,
                    "lastEdit": "2021-02-26T10:05:09.562Z",
                    "latestReply": "2021-02-26T10:07:50.842Z",
                    "latestReplyUserId": "5bb762ed066d1b001d5289f2",
                },
                {
                    "id": "5d985998cdb666001ef52837",
                    "title": "Nya Loading fyller 1 år!",
                    "body": '![](https://i.imgur.com/vQladDr.png)\n\n### **TACK FÖR DET HÄR ÅRET!**\nAtt Loading som från ingenstans stängde ned i maj 2018 kom för oss alla som en chock. Hur 13 år av forumhistoria kunde försvinna så plötsligt var ledsamt, tragiskt och till och med upprörande. Spelforumet var inte bara ännu en mötesplats i spelsverige, under dessa gångna år hade det blivit en del av mångas vardag. Det fanns däremot de som inte ville acceptera hemsidans öde, handlingskraftiga individer som var redo att gå vidare efter detta missöde.\n\nFör exakt ett år sedan påbörjade vi en resa tillsammans med er forumiter. Vi gick hand i hand från gammalt till nytt och lyckades med gemensamt engagemang återuppliva vår gemenskap. Det har självklart inte alltid varit en lätt resa, och ingen av oss var nog helt säkra på vart vi var på väg, men nog har det varit roligt också. Därför vill vi självklart tacka er alla för att ni fortsätter att vara med på Loading.se i vått och torrt. Er som följde med oss från det gamla forumet dit vi är idag, er som under det gångna året fyllt forumet med intressanta diskussioner och heta debatter.\n\nLoading har alltid handlat om användarna - ni som varje dag besöker forumet, och deltar i hjärtliga diskussioner om tv-spel och andra ämnen. Det är ni som under alla dessa år hållit Loadings flamma levande, och aldrig har det påståendet varit mer sant än nu. Idag drivs hemsidan av en fristående grupp eldsjälar och upprätthålls tack vare generösa donationer från våra användare. Ett extra stort tack går därför ut till alla er som stöttar forumet på Patreon. Utan era bidrag hade inget av detta varit möjligt!\n\nLåt oss nu, med ett helt år av forumeskapader i backspegeln, blicka framåt till ytterligare ett framgångsrikt och spännande år i Loadings tecken! Skål!\n\n### **FORUMETS FÖRSTA ÅR I SIFFROR**\n33433 inlägg har postats\n446 unika trådar har skapats\n219 redaktionella recensioner har publicerats\n1 falsk DO-anmälning mot forumet har skapats \n\n### **ÅRETS BÄSTA TRÅDAR**\n\n**[Trådlek - En series bästa spel (The Legend of Zelda)](https://loading.se/post/5d6e5fbb3cc708001eaaf00c) av Jocke Andersson**\nEn av vårt första års bästa trådar som lyckades låta oss rannsaka våra åsikter på ett nyskapande sätt. Att jämföra alla titlar i en hel spelserie gjorde detta till en underhållande övning i att döda sina älsklingar.\n\n**[The Bullshit Lounge](https://loading.se/post/5bb7aa488fef22001d902643) av Avgrundsvrål**\nLoadings hjärta förstås. Med 530 sidor och över 15300 inlägg finns det ingenting som kan stoppa denna outtömliga källa av skräppost. \n\n**[Fikabröd](https://loading.se/post/5cebf2a48b0a87001db38d7d) av Kiki**\nDen officiella tråden om allt gott vi käkar till fikan. \n\n**[Loading blir serie!](https://loading.se/post/5bc0c65911b2c9001d2b3b03) av Avgrundsvrål**\nTråden där vi under året kunnat illustrera vad som hänt på forumet i form av serier. En underhållande liten tråd som behöver mer uppmärksamhet!\n\n**[Presentera det mest fantastiska underskattade spelet](https://loading.se/post/5beb217d033bb1001db3fff2?fbclid=IwAR3i6WREsjvQJqhAOgX5Zrfu6mHfslZ6vQ45N3ODR1yLwFrGRcYz_D1NphU) av Aleksandar Buntic**\nDenna tråd om underskattade spel blev snabbt fylld med en hel del märkliga och spännande titlar som många kanske missat. Värd att ta en titt på om ni vill ha intressanta tips om vad som bör spelas.\n\n**[Opopulära spelåsikter - vilka är dina?](https://loading.se/post/5beb217d033bb1001db3fff2?fbclid=IwAR3i6WREsjvQJqhAOgX5Zrfu6mHfslZ6vQ45N3ODR1yLwFrGRcYz_D1NphU) av Alexander Rehnman**\nEn tråd full med individer som har fel.\n\n**[LLLLINK BBBREAKER!! (Nintendo)](https://loading.se/post/5cd8854de30c54001d547fea) av Shiine**\nBildlekar engagerar alltid på ett eller annat sätt, speciellt om de låter en flexa med sin spelsamling på kuppen.\n\n**[Charles Martinet hävdar att Mario inte alls säger "So long, gay Bowser!”](https://loading.se/post/5cc7043316aff9001dee48bc) av Alexander Rehnman**\nVi blev också chockerade när vi hörde det. Fullkomligt orimligt.\n\n**[Varför är folk så rädda för lägre svårighetsgrader/tillgänglighetsalternativ?](https://loading.se/post/5caca66c1c55ff001d4e97df) av Alexander Rehnman**\nKonstnärliga intentioner och tillgänglighet ställs som totala motpunkter i denna diskussion om svårighetsgrader inom spel. Pajkastning och debatt på hård nivå.\n\n**[Kulturmarxistisk Gillette-reklam propagerar för att mörda alla män!](https://loading.se/post/5c41e1348282b8001d941433) av Avgrundsvrål**\nPolitik, rakning och PR-trick allt i en och samma tråd. En helt vanlig strid på idéernas slagfält.\n\n**[Duscha på morgonen vs duscha på kvällen](https://loading.se/post/5c9baf2a327359001d38683f) av Erik**\nVår tids kanske viktigaste fråga besvarad av forumiterna!\n\n**[Kärlekstråden!](https://loading.se/post/5c3cb495473055001dadbb3c) av Notorious Gamer**\nTråden där vi delade med oss av våra kärlekseskapader under året som gått. Brustna hjärtan, nyfunnen förälskelse och andra intriger väntar i denna dramafyllda forumtråd.\n\n![](https://i.imgur.com/6zl9mey.png)\n',
                    "category": "other",
                    "coverImage": "https://i.imgur.com/vQladDr.png",
                    "postType": "update",
                    "createdAt": "2019-10-05T08:51:36.754Z",
                    "updatedAt": "2020-10-06T08:08:12.197Z",
                    "userId": "5bb7aa868fef22001d902665",
                    "replies": 47,
                    "edits": 2,
                    "lastEdit": "2019-10-05T08:58:22.115Z",
                    "latestReply": "2020-10-06T08:08:12.195Z",
                    "latestReplyUserId": "5bb7a8b2066d1b001d528a5f",
                },
                {
                    "id": "62463d47b37f8b2ab9ac906e",
                    "title": "Styr Loading med din röst",
                    "body": "Vi har länge snickrat på lösningar som tar Loading in i finrummet och blir en naturlig del av din vardag. Därför har vi utvecklat en Google Assistant app där du kan prata med Loading.se.\n\nMan kommer åt den via sin Android-telefon, Google Nest/Home eller Google Assistant appen på iPhone. Se till att ha lagt till Svenska bland språken du vill prata på.\n\nMan börjar diskussionen med **Prata med Loading.se**, efter det finns det en rad kommandon man kan leka med.\n\n- Man kan fråga efter de **senaste artiklarna**, då listar de tre senaste\n- Sedan kan du be den att läsa den **första, andra eller tredje** av dessa\n- Ber man den att **söka efter** något läser den upp en bit av det inlägg som matchade bäst, att söka efter *gandalf* är alltid en hit\n- Sist men inte minst lanserar vi äntligen funktionen att få höra hur många trådar och inlägg som finns på Loading, be bara att få höra om den **totala statistiken**\n\nAppen vill gärna hålla dig kvar i konversationen så man kan avsluta genom att inte prata med den på ett tag eller helt enkelt säga **hejdå** eller **adjö**.\n\nMan kan också komma direkt till en funktion genom att säga **Prata med Loading.se om de senaste nyheterna**.\n\nHoppas ni kommer ha mycket kul genom att prata med Loading.se\n\n[Kolla in appen på sidan för Google Assistant](https://assistant.google.com/services/a/uid/0000003c159950f9?hl=sv_se)",
                    "category": "other",
                    "coverImage": "5f46bc88-4d03-448a-84c9-fec7e021eda2.jpg",
                    "postType": "update",
                    "createdAt": "2022-03-31T23:46:15.499Z",
                    "updatedAt": "2022-04-07T06:44:51.084Z",
                    "userId": "5bb7ae3d8fef22001d90276e",
                    "replies": 9,
                    "latestReply": "2022-04-07T06:44:51.083Z",
                    "latestReplyUserId": "5bb7a8b2066d1b001d528a5f",
                },
                {
                    "id": "5bbcb23d2e1d32001d523816",
                    "title": "Tack Loading",
                    "body": '# UPPDATERING\n\n## Kära Loadingvänner! \n\n\nVi vill först börja med att tacka er för en fantastisk lanseringshelg. Den fantastiskt trevliga och positiva stämning som rått och hur pass väl allt har fungerat, spartanskt utförande till trots, värmer våra hjärtan. \n\n\nEr feedback är otroligt värdefull. Just nu ligger störst fokus vid att, i den takt det är möjligt för vår hjälte Stanislav Izotov, rätta till diverse frågetecken och se till att den grundläggande upplevelsen blir så smidig som möjligt. På lång sikt kommer ni att vara en del av hur vårt community utformas.\n\n\n**Vi vill ta detta tillfälle i akt att förklara varför vi valde att lansera nya Loading i ett så ofärdigt skick.**\n\n\nDet handlar om två saker:\n\n\nDet viktigaste är för att vi vill att ni ska känna att ni har möjlighet att direkt påverka utvecklingen och känna er som en del av hela upplevelsen. Att innerst inne veta att alla ni som kommenterat kring saker också sett till att de har blivit till verklighet. Det gäller även er som stöttar oss via Patreon, vilket visar att ni vill se att vi lyckas. Det ger oss en möjlighet att skapa den mötesplats och arena vi vill tillsammans med er, även om ni inte uttrycker det i text.\n\n\nDet andra är för att vi som jobbat med detta projekt i runt fyra månader nu och behövde en milstolpe för att fortsätta sträva framåt, hitta ny energi och motivation - att helt enkelt få en bekräftelse på att det var möjligt och att ni fortfarande var med oss!\n\n\nTill sist vill vi också lägga vikt vid att nämna att ni inte ska känna er oroliga för att era inlägg ska stryka på foten när sidan genomgår sin metamorfos längs vägen. Trots att sidan är som den är och att rätt stora förändringar kommer att ske, kommer alla era inlägg finnas kvar tack vare den molnbaserade serverlösning vi har valt att använda. Det går knappt beskriva skillnaden att bygga en sådan här tjänst idag jämfört med hur det var för 10-20 år sedan.\n\n\n![alt text](https://i.imgur.com/zSHYABw.png"pixelhjärta.jpg")\n\n\n__Redaktionen__',
                    "category": "other",
                    "coverImage": "https://i.imgur.com/Ycrx9Ci.jpg",
                    "postType": "update",
                    "createdAt": "2018-10-09T13:50:53.896Z",
                    "updatedAt": "2018-10-14T04:36:51.558Z",
                    "userId": "5bb751cb066d1b001d5289e0",
                    "replies": 12,
                    "latestReply": "2018-10-14T04:36:51.556Z",
                    "latestReplyUserId": "5bb7ab038fef22001d902690",
                },
                {
                    "id": "5f27b945077189001e59f6a9",
                    "title": "Tävling – Vinn Dreams till PS4!",
                    "body": "![](https://i.imgur.com/zd2gINa.png)\n\nVi i Loading-redaktionen tävlar nu ut tre exemplar av Dreams till Playstation 4. Tävlingen går ut på att du ska beskriva en dröm som du har haft och som du skulle vilja bygga upp i spelet. Vi kommer sedan att välja ut tre lyckliga vinnare som får varsitt exemplar.\n\n**Så här gör du för att delta:**\n\nBeskriv en dröm du har haft och som du skulle vilja bygga upp i spelet.\nSkicka in ditt bidrag till info@loading.se med ämnesraden “Dreams tävling”. På så sätt får vi din e-postadress så vi lätt kan kontakta dig ifall du vinner. Se till att skriva ditt Loading-namn antingen i ämnesraden eller i själva meddelandet. \nLägg upp ditt bidrag i denna tråd. Det är frivilligt, men det uppmuntras!\nHåll tummarna för att du vinner!\n\n\nDu har fram till 10 augusti på dig att skicka in ditt bidrag.\n\nLycka till!\n\n![](https://i.imgur.com/6zl9mey.png)\n\n",
                    "category": "games",
                    "coverImage": "https://i.imgur.com/zd2gINa.png",
                    "postType": "update",
                    "createdAt": "2020-08-03T07:14:13.547Z",
                    "updatedAt": "2020-08-03T07:14:13.547Z",
                    "userId": "5bbd0e7403dc9d001d9a5565",
                    "replies": 0,
                },
                {
                    "id": "60c71783cf57f0001e80cb0d",
                    "title": "Tävling: Vinn Mass Effect Legendary Edition till Xbox!",
                    "body": "![](https://i.imgur.com/NHxClYQ.png)\n\nVi i redaktionen har fått ett exemplar av Mass Effect: Legendary Edition till Xbox att tävla ut till en lycklig forumit.\n\nOm du vill få chansen att ge dig ut i rymden med Shepard, Garrus och gänget – för första eller femtioelfte gången – är reglerna enkla:\n\nRita ditt eget rymdskepp och skicka ditt bidrag till info@loading.se (så vi har din e-postadress om du vinner) senast **klockan 23.59 svensk tid den 21 juni 2021**. Märk ditt mail med “Mass Effect”. Det måste inte vara ett rymdskepp som passar in i Mass Effects universum, utan det är bara din egen fantasi som sätter gränserna. Posta gärna bidraget i den här tråden också!\n\nDet bästa rymdskeppet väljs sedan ut av oss i redaktionen.\n\nLycka till!\n\n![](https://i.imgur.com/6zl9mey.png)\n",
                    "category": "games",
                    "coverImage": "https://i.imgur.com/NHxClYQ.png",
                    "postType": "update",
                    "createdAt": "2021-06-14T08:46:59.250Z",
                    "updatedAt": "2021-07-01T18:56:20.485Z",
                    "userId": "5bbd0e7403dc9d001d9a5565",
                    "replies": 14,
                    "latestReply": "2021-07-01T18:56:20.485Z",
                    "latestReplyUserId": "5bb7a9f98fef22001d902604",
                },
                {
                    "id": "5bcf4aca44b859001dad8c66",
                    "title": "Vill du recensera Dark Souls Remastered för Loading?",
                    "body": "# Recensionsuppdrag: Dark Souls Remastered\n**Format: Nintendo Switch**\n\nHej allihopa! Vi tänkte att vi skulle testa på ett nytt spännande koncept här på forumet. För att bygga vidare på vår härliga forumkultur och det som gör oss unika tänkte vi testa på att dela ut ett recensionsuppdrag till en av våra läsare.\n\nVi vill helt enkelt ge något tillbaka till er forumiter som är med och bidrar till att Loading är det fantastiska forum som vi har idag. \n\nVi tror att det här skulle kunna leda till någonting väldigt spännande. Någonting som vi inte har gjort förut.\n\nVi har fått ett recensionsexemplar av Dark Souls Remastered från Bergsala och har förstås haft en dialog med utgivaren om den här idén. \n\nDet kommer givetvis att ställas samma krav på text som när vi delar ut ett recensionsuppdrag till den riktiga redaktionen. Samma förutsättningar, samma krav på deadline och texten kommer att behöva korrläsas av redaktionen innan vi publicerar (här är det också bra att tänka på att du kommer att behöva skriva under recensionen med ditt riktiga namn).\n\nSå vad säger du? Är du intresserad av att recensera Dark Souls Remastered för Loadings räkning?\n\nI sådana fall, skriv en rad om vem du är och kanske vilket förhållande du har till serien.\n\nVi behöver ha ditt svar senast fredagen den 26/10.\n\nEfter det kommer vi att välja ut ett av namnen som har anmält sitt intresse.\n\nmed vänliga hälsningar, Redaktionen",
                    "category": "games",
                    "coverImage": "https://i.imgur.com/IhhUC15.jpg",
                    "postType": "update",
                    "createdAt": "2018-10-23T16:22:34.747Z",
                    "updatedAt": "2018-11-10T07:23:45.157Z",
                    "userId": "5bb77830066d1b001d528a1c",
                    "replies": 41,
                    "latestReply": "2018-11-10T07:23:45.155Z",
                    "latestReplyUserId": "5bb751cb066d1b001d5289e0",
                },
                {
                    "id": "5bb7a7de066d1b001d528a5c",
                    "title": "Välkommen till Loading",
                    "body": "![Välkommen till Loading](https://i.imgur.com/KwIAdW7.jpg)\n\n# Loading\n#\n#\n.. har alltid varit en plats som är så mycket mer än ett forum på internet. För många av oss har Loading varit ett naturligt inslag i vardagen ända sedan mitten av 00-talet. En mötesplats för att diskutera allt möjligt, umgås eller bara läsa på om de senaste nyheterna i spelbranschen.\n\nNär Loading försvann i början av den här sommaren skapades ett tomrum. Direkt därefter samlades redaktionen och påbörjade samtalet om den framtid som vi nu äntligen skymtar.\n\nNär vi fick möjligheten att ta över varumärket för Loading och börja om tog vi den, för att vi fortfarande tror på att det finns ett behov av en sådan här mötesplats på internet.\n\nArbetet startade och loggan och designen föddes. Vi fick hjälp med att bygga upp sidan från grunden. Av det gamla finns ingenting kvar förutom drömmen och den kan ingen ta ifrån oss. Vi vill att Loading ska fortsätta vara ett rum för inkludering, för gemenskap och för en värdegrund där alla har samma rätt att delta.\n\nVårt nya Loading kommer att fortsätta utvecklas, men för att kunna hålla drömmen vid liv så kommer vi alla att vara viktigare än någonsin förr. Reset Media är inte längre med i bilden. Loading kommer att drivas av Patreon. Forum kostar och vi kommer att behöva hjälpas åt för att skapa det här. Vi hoppas att du vill hjälpa till och bidra. Det behövs inte så mycket om många är med.\n\nVi vill också passa på att säga tack för att du finns, för att det är du som driver oss framåt.\n\nNu sätter vi igång.\n\n#### Välkommen!\n\n#\n#\nPatreon: http://loading.se/post/5bb797b8066d1b001d528a43  \nOrdning- och trivselregler: http://loading.se/post/5bb76fb0066d1b001d528a11  \nHur funkar nya Loading: http://loading.se/post/5bb78aba066d1b001d528a30  \nDen stora förslagstråden: http://loading.se/post/5bb790e5066d1b001d528a3a  \n\nMed varma hälsningar, Redaktionen\n",
                    "category": "other",
                    "coverImage": "https://i.imgur.com/KwIAdW7.jpg",
                    "postType": "update",
                    "createdAt": "2018-10-05T18:05:18.889Z",
                    "updatedAt": "2021-06-24T17:51:36.316Z",
                    "userId": "5bb75ec2066d1b001d5289e9",
                    "replies": 59,
                    "latestReply": "2021-06-24T17:51:36.316Z",
                    "latestReplyUserId": "5bb7b1ac8fef22001d902820",
                },
            ],
            "users": [
                {
                    "id": "5bbd0e7403dc9d001d9a5565",
                    "name": "Redaktionen",
                    "picture": "eb3f2b33-c557-4042-8d5b-4075f8803761.png",
                    "role": "editor",
                    "createdAt": "2018-10-09T20:24:20.486Z",
                    "status": "active",
                },
                {
                    "id": "5bb7e4ab8fef22001d902cb9",
                    "name": "n e o v i o l e n c e",
                    "picture": "2a3b84af-dcfe-4aff-8b36-1416729f7958.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T22:24:43.647Z",
                    "status": "active",
                },
                {
                    "id": "5bb7b1ac8fef22001d902820",
                    "name": "soar",
                    "picture": "d96f110f-c140-4845-b394-15e9c557e088.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:47:08.568Z",
                    "status": "active",
                },
                {
                    "id": "5bb7ae3d8fef22001d90276e",
                    "name": "Stan64",
                    "picture": "032f8967-f6ef-4fc3-9ac9-6d0b04194a0f.png",
                    "role": "editor",
                    "createdAt": "2018-10-05T18:32:29.672Z",
                    "status": "active",
                },
                {
                    "id": "5bb7ab038fef22001d902690",
                    "name": "Metatron",
                    "picture": "c10b245d-56b3-4f2b-b165-eec55a38b3ec.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:18:43.176Z",
                    "status": "active",
                },
                {
                    "id": "5bb7aa868fef22001d902665",
                    "name": "Kiki",
                    "picture": "8b0e6e55-6b4a-4386-8551-e510b5e62fd4.png",
                    "role": "user",
                    "createdAt": "2018-10-05T18:16:38.350Z",
                    "status": "active",
                },
                {
                    "id": "5bb7a9f98fef22001d902604",
                    "name": "Joe E Tata",
                    "picture": "523008b9-aa0b-44f2-8376-f381ee920117.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T18:14:17.021Z",
                    "status": "active",
                },
                {
                    "id": "5bb7a8b2066d1b001d528a5f",
                    "name": "Sarato",
                    "picture": "ef3d90ec-b6fc-46b8-8265-a2829706164f.jpg",
                    "role": "moderator",
                    "createdAt": "2018-10-05T18:08:50.282Z",
                    "status": "active",
                },
                {
                    "id": "5bb77830066d1b001d528a1c",
                    "name": "Elin Ekberg",
                    "picture": "a97bf0c2-4de3-4888-8acc-78f9b58e65dc.png",
                    "role": "user",
                    "createdAt": "2018-10-05T14:41:52.609Z",
                    "status": "active",
                },
                {
                    "id": "5bb762ed066d1b001d5289f2",
                    "name": "Aleksandar Buntic",
                    "picture": "116c4d02-919e-468c-9191-3bebabf2f665.png",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:11:09.961Z",
                    "status": "active",
                },
                {
                    "id": "5bb7618d066d1b001d5289ef",
                    "name": "Niklas Karlsson",
                    "picture": "c8f27420-089e-4f9a-adf9-8b7c9fb85d4a.png",
                    "role": "editor",
                    "createdAt": "2018-10-05T13:05:17.573Z",
                    "status": "active",
                },
                {
                    "id": "5bb75ec2066d1b001d5289e9",
                    "name": "Aaron Vesterberg Ringhög",
                    "picture": "b44e7341-421f-48fb-81fc-331acd93ba34.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T12:53:22.371Z",
                    "status": "active",
                },
                {
                    "id": "5bb751cb066d1b001d5289e0",
                    "name": "Isabell Rydén",
                    "picture": "b12a2fe1-101e-4ee3-9679-941b24b02e20.jpg",
                    "role": "editor",
                    "createdAt": "2018-10-05T11:58:03.230Z",
                    "status": "active",
                },
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = api.get_editorials(page=1, post_type="update", sort="title")

        self.assertEqual(response.get("code"), 200)
        self.assertEqual(response.get("message"), "OK")
        self.assertDictEqual(response.get("data"), expected_response)

        threads = response.get("data").get("posts")

        for thread in threads:
            self.assertEqual(thread.get("postType"), "update")

    @patch("loading_sdk.api.requests")
    def test_get_editorials_failure_page_too_low(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too low",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = response = api.get_editorials(
            page=-1,
            post_type="update",
            sort="title",
        )

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_get_editorials_failure_page_too_high(self, mock_requests):
        status_code = 404
        expected_response = {
            "code": status_code,
            "message": "Page number too high",
            "data": {"posts": [], "users": []},
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"posts": [], "users": []}
        mock_requests.get.return_value = mock_response

        api = LoadingApiClient()
        response = response = api.get_editorials(
            page=999,
            post_type="update",
            sort="title",
        )

        self.assertDictEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
    def test_edit_post_success(self, mock_requests, mock_authenticate):
        status_code = 200
        expected_response = {
            "id": "000000000000000000000000",
            "body": "updated message",
            "postType": "regular",
            "createdAt": "2022-01-01T00:00:00.000Z",
            "updatedAt": "2022-01-02T00:00:00.000Z",
            "parentId": "222222222222222222222222",
            "userId": "111111111111111111111111",
            "replies": 0,
            "edits": 1,
            "lastEdit": "2022-01-02T00:00:00.000Z",
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.patch.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        # Edit post.
        api = LoadingApiClient("test@email.com", "password")
        response = api.edit_post(
            post_id="000000000000000000000000",
            message="updated message",
        )

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 200)
        self.assertDictEqual(response.get("data"), expected_response)

        # Edit thread.
        api = LoadingApiClient("test@email.com", "password")
        response = api.edit_thread(
            thread_id="000000000000000000000000",
            message="updated message",
        )

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 200)
        self.assertDictEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.requests")
    def test_edit_post_failure_no_auth_token(self, mock_requests):
        status_code = 401
        expected_response = {"code": status_code, "message": "No auth token"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.patch.return_value = mock_response

        # Edit post.
        api = LoadingApiClient()
        response = api.edit_post(post_id="post_id_to_edit", message="updated message")

        self.assertEqual(response, expected_response)

        # Edit thread.
        api = LoadingApiClient()
        response = api.edit_thread(
            thread_id="thread_id_to_edit",
            message="updated message",
        )

        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_edit_post_failure_post_does_not_exist(self, mock_requests):
        status_code = 404
        expected_response = {"code": status_code, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.patch.return_value = mock_response

        # Edit post.
        api = LoadingApiClient()
        response = api.edit_post(
            post_id="non_existing_post_id",
            message="new updated message",
        )

        self.assertEqual(response, expected_response)

        # Edit thread.
        api = LoadingApiClient()
        response = api.edit_thread(
            thread_id="non_existing_thread_id",
            message="new updated message",
        )

        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    def test_edit_post_failure_empty_message(self, mock_authenticate):
        expected_response = {
            "code": 400,
            "message": '"message" is not allowed to be empty',
        }

        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        # Edit post.
        api = LoadingApiClient("test@email.com", "password")
        response = api.edit_post(post_id="existing_post_id", message="")

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response, expected_response)

        # Edit thread.
        api = LoadingApiClient("test@email.com", "password")
        response = api.edit_thread(thread_id="existing_thread_id", message="")

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    def test_create_post_failure_empty_thread_id(self, mock_authenticate):
        expected_response = {
            "code": 400,
            "message": '"thread_id" is not allowed to be empty',
        }

        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiClient("test@email.com", "password")
        response = api.create_post(thread_id="", message="New message")

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
    def test_create_post_failure_thread_id_does_not_exist(
        self, mock_requests, mock_authenticate
    ):
        status_code = 404
        expected_response = {"code": status_code, "message": "Post does not exist"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiClient("test@email.com", "password")
        response = api.create_post(
            thread_id="non_existing_thread_id",
            message="New message",
        )

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_create_post_failure_no_auth_token(self, mock_requests):
        status_code = 401
        expected_response = {"code": status_code, "message": "No auth token"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiClient()
        response = api.create_post(
            thread_id="existing_thread_id", message="New message"
        )

        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
    def test_create_post_success(self, mock_requests, mock_authenticate):
        status_code = 201
        expected_response = {
            "id": "000000000000000000000000",
            "body": "New message!",
            "postType": "regular",
            "createdAt": "2022-01-01T00:00:00.000Z",
            "updatedAt": "2022-01-02T00:00:00.000Z",
            "parentId": "111111111111111111111111",
            "userId": "222222222222222222222222",
            "replies": 0,
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiClient("test@email.com", "password")
        response = api.create_post(
            thread_id="111111111111111111111111",
            message="New message!",
        )

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 201)
        self.assertEqual(response.get("data"), expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
    def test_create_thread_success(self, mock_requests, mock_authenticate):
        status_code = 201
        expected_response = {
            "id": "000000000000000000000000",
            "body": "updated message",
            "postType": "regular",
            "createdAt": "2022-01-01T00:00:00.000Z",
            "updatedAt": "2022-01-02T00:00:00.000Z",
            "parentId": "222222222222222222222222",
            "userId": "111111111111111111111111",
            "replies": 0,
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiClient("test@email.com", "password")
        response = api.create_thread(
            title="Hello",
            message="My message",
            category_name="other",
        )

        self.assertIsNotNone(api._cookies)
        self.assertEqual(api._cookies, self.cookie_jar)
        self.assertEqual(response.get("code"), 201)
        self.assertDictEqual(response.get("data"), expected_response)

    def test_create_thread_failure_invalid_category(self):
        expected_response = {"code": 400, "message": "Invalid forum category"}

        api = LoadingApiClient()
        response = api.create_thread(
            title="Hello",
            message="My message",
            category_name="invalid_category",
        )

        self.assertEqual(response, expected_response)

    def test_create_thread_failure_invalid_post_type(self):
        expected_response = {"code": 400, "message": "Invalid post_type"}

        api = LoadingApiClient()
        response = api.create_thread(
            title="Hello",
            message="My message",
            category_name="other",
            post_type="invalid_post_type",
        )

        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.LoadingApiClient._authenticate")
    @patch("loading_sdk.api.requests")
    def test_create_thread_failure_empty_title_or_message(
        self, mock_requests, mock_authenticate
    ):
        status_code = 400
        expected_response = {
            "code": status_code,
            "message": "Validation error",
            "errors": [
                {
                    "field": "title",
                    "location": "body",
                    "messages": ['"title" is not allowed to be empty'],
                    "types": ["any.empty"],
                },
                {
                    "field": "body",
                    "location": "body",
                    "messages": ['"body" is not allowed to be empty'],
                    "types": ["any.empty"],
                },
            ],
        }

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response
        mock_authenticate.return_value = {"code": 200, "cookies": self.cookie_jar}

        api = LoadingApiClient("test@email.com", "password")
        response = api.create_thread(
            title="",
            message="",
            category_name="other",
        )

        self.assertEqual(response, expected_response)

    @patch("loading_sdk.api.requests")
    def test_create_thread_failure_no_auth_token(self, mock_requests):
        status_code = 401
        expected_response = {"code": status_code, "message": "No auth token"}

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = expected_response
        mock_requests.post.return_value = mock_response

        api = LoadingApiClient()
        response = api.create_thread(
            title="Hello",
            message="My message",
            category_name="other",
        )

        self.assertEqual(response, expected_response)
