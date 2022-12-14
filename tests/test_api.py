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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
    def test_search_success(self, mock_requests):
        expected_response = {
            "posts": [
                {
                    "parentId": "5c6d3faae34cd5001ddf33f4",
                    "body": "??r det bara jag som f??tt k??nslan av att Leia inte k??nner eller har tr??ffat Obi-Wan i A New Hope? Hon verkar inte bry sig n??mnv??rt n??r han d??r och mycket mindre ??n Luke, som k??nt honom i en halv kvart. I hennes meddelande i R2-D2 s??ger hon dessutom att det ??r hennes far som ber Obi-Wan att hj??lpa henne, med repliker som l??ter som att hon inte har n??gon relation till honom. ",
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
                    "name": "Anders Ekl??f",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
    def test_get_thread_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5f9e4e8c2c32e2001ed17170",
                    "title": "Spelmusik samplad i l??tar",
                    "body": "Har ni uppt??ckt n??gra samples fr??n spelmusik n??r ni suttit och lyssnat p?? ''vanlig'' musik?\n\nDela med er av era uppt??ckter!\n\nB??rjar med en l??t fr??n den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat s??kerst??lla det men visst m??ste v??l det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\n??r det ??ven ljudeffekter fr??n Link d??r vid 02:32, om jag h??r r??tt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget fr??n Castlevania II. \nDet tog n??stan pinsamt nog n??gra genomlyssningar innan det klickade, l??tarna har ju f??r fan samma namn ocks?? haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget fr??n f??rsta Medal of Honor - Rjuken Sabotage. Denna var sv??rare, fick bara en k??nsla att den var fr??n ett spel och s??kte d?? upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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
                    "body": "Tror inte det b??r vara helt om??jligt att typ k??ra m??nster efter tredjedelar eller typ gyllene snittet. Ha olika ankarpunkter som betygen kan kretsa runt. T??nker dock att i en helt ??ppen l??sning d??r bilder mest delas p?? internet s?? kommer graderingen g??ras helt i interagering med andra anv??ndare, l??ta det hela bli lite mer subjektivt, liksom.",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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
                    "title": "Spelmusik samplad i l??tar",
                    "body": "Har ni uppt??ckt n??gra samples fr??n spelmusik n??r ni suttit och lyssnat p?? ''vanlig'' musik?\n\nDela med er av era uppt??ckter!\n\nB??rjar med en l??t fr??n den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat s??kerst??lla det men visst m??ste v??l det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\n??r det ??ven ljudeffekter fr??n Link d??r vid 02:32, om jag h??r r??tt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget fr??n Castlevania II. \nDet tog n??stan pinsamt nog n??gra genomlyssningar innan det klickade, l??tarna har ju f??r fan samma namn ocks?? haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget fr??n f??rsta Medal of Honor - Rjuken Sabotage. Denna var sv??rare, fick bara en k??nsla att den var fr??n ett spel och s??kte d?? upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
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

    @patch("loading_sdk.sync_api.client.requests")
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
                    "title": "Spelmusik samplad i l??tar",
                    "body": "Har ni uppt??ckt n??gra samples fr??n spelmusik n??r ni suttit och lyssnat p?? ''vanlig'' musik?\n\nDela med er av era uppt??ckter!\n\nB??rjar med en l??t fr??n den gamla fjortisfavoriten Byz, Byz - Respekt. Har inte kunnat s??kerst??lla det men visst m??ste v??l det vara ett sample av Mike Tyson's Punch-Out! - Fight Theme https://youtu.be/VE8vKLEK6A8 ?\nhttps://youtu.be/EnBHwl8-bf4\n??r det ??ven ljudeffekter fr??n Link d??r vid 02:32, om jag h??r r??tt?\n\nArmy of the Pharaohs - Bloody Tears. Sample taget fr??n Castlevania II. \nDet tog n??stan pinsamt nog n??gra genomlyssningar innan det klickade, l??tarna har ju f??r fan samma namn ocks?? haha!\nhttps://youtu.be/rrJbpJwmQJc\nhttp://youtu.be/e2oZtvjg5oA\n\nHeavy Metal Kings - Splatterfest. Sample taget fr??n f??rsta Medal of Honor - Rjuken Sabotage. Denna var sv??rare, fick bara en k??nsla att den var fr??n ett spel och s??kte d?? upp svaret.\nhttps://youtu.be/1VuVyfmPUd8\nhttps://youtu.be/tdWt-wl-wuw\n",
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

    @patch("loading_sdk.sync_api.client.requests")
    def test_get_games_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bb9c9911f1848001d97f202",
                    "title": "Ska spel problematisera sig sj??lva?",
                    "body": '# S02A39 "Virtuell skr??ckstrategi"\n#### Aaron och Amanda f??r f??rst??rkning fr??n redaktionen i form av meriterade Alexander Rehnman samt VR-experterna Johan Lorentzon och Petter Arbman i veckans avsnitt!\n\n![bild](https://i.imgur.com/fdTxqmS.png)\n\nLoading ??r ??ntligen h??r!\n\nOch hur vill vi fira det p?? b??sta s??tt om inte genom att bjuda in Johan Lorentzon, Alexander Rehnman och Petter Arbman fr??n redaktionen, f??r att snacka japansk kultur p?? 3DS och skr??ck-??ventyr samt strategiskjutare i den virtuella verkligheten?\n\nAmanda reflekterar h??gt och l??gt ??ver Shadow of the Tomb Raider och Aaron ??ver Forza Horizon 4 p?? ett s??tt som g??r att en funderar p?? om de b??da inte har spelat n??got annat de senaste veckorna (Pst! Det har de ju n??stan inte heller!).\n\nGl??m inte att svara p?? Veckans Fr??ga som denna veckan tar avstamp i v??rt samtal runt Shadow of the Tomb Raider!\n##### "??r det bra att spel kommenterar p?? sin egen problematik?"\n#\nG??R DIN R??ST H??RD [H??R!](https://polldaddy.com/poll/10129492/)\n#\n#\n\nH??r hittar du TV-spelspodden:\n* [Twitter](https://twitter.com/TVspelspodden)\n* [Facebook](https://www.facebook.com/TVspelspodden/)\n* [Instagram](https://www.instagram.com/tvspelspodden/)\n* [Mail](mailto:info@tv-spelspodden.se)\n* [Arvik f??r samtliga avsnitt](http://tv-spelspodden.se/)\n* [Youtube](https://www.youtube.com/channel/UCh_NLZ9fbDFRk0zy8sq0Q3w?view_as=subscriber)\n* [Twitch](https://www.twitch.tv/tvspelspodden)\n\nPrenumerera:\n* [RSS-feed](http://tvspelspodden.libsyn.com/rss)\n* [iTunes](https://itunes.apple.com/se/podcast/tv-spelspodden/id1249509863?mt=2)',
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
                    "title": "Vad VILL ni se h??rn??st fr??n Rocksteady?",
                    "body": "Det har varit mycket surr om London-studion den senaste tiden. Allt fr??n Batman till Harry Potter och TMNT. Men om vi sl??nger alla fakta ut genom f??nstret och bara letar inom oss sj??lva, vad VILL ni se h??rn??st fr??n studion?",
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
                    "title": "Ett spel. En dr??m.",
                    "body": "Jag vaknar.\n\n..varmt..\n\nkollar p?? klockan\n\n..??ngest..\n\nSluter ??gonen\n\n..medelhavet..\n\nPl??tsligt ??r jag d??r\n\nJag och mitt skepp p?? ??ppet hav\n\nP?? v??g\n\nP?? ??ventyr\n\n..K??rlek..\n\nFint va?\n\nHar du dr??mt om tv-spel n??gon g??ng? ",
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
                    "title": "Skybound Games g??r klart The Walking Dead",
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
                    "body": "# Douglas Lindberg recenserar Forza Horizon 4\n#### Xbox One\n\n![F1](https://i.imgur.com/FidNKS5.png)\n\nForza Horizon har alltid legat mig varmt om hj??rtat. Jag minns fortfarande n??r det f??rsta spelet sl??pptes och vilken kontrast det var mot de mer seri??sa Motorsport-utg??vorna. \n\nDet var sex ??r sen. \n\nOch nu n??r det fj??rde spelet i serien ??r h??r s?? ??r det sv??rt att inte imponeras av den relevans som serien fortfarande har.\n\nForza Horizon 4 ??r en arkadracer som utspelar sig i en ??ppen v??rld med m??ngder av t??vlingar, utmaningar och hemligheter att uppt??cka. Prestationer ger dig erfarenhet och erfarenhet ger dig bel??ningar i form av nya bilar. Just den h??r upplagan inneh??ller ungef??r 450 stycken vilket b??r r??cka f??r att h??lla en sysselsatt ett tag fram??ver.\n\nSpelet ??r ??verlag v??ldigt likt sina f??reg??ngare, men det finns en del system som ??r f??r??ndrade. Skill points ??r exempelvis bundna till bilarna ist??llet f??r till din karakt??r, alla events kan k??ras solo eller i co-op med andra och nya t??vlingar l??ses upp n??r du samlar erfarenhet i varje enskild kategori. K??r du till exempel banrace l??ser du upp nya banrace och inget annat. \n\nOm de h??r systemen ??r b??ttre eller s??mre ??n f??rut ??r en smaksak. Det nya uppl??gget ger ??tminstone en fr??sch pr??gel ??t konceptet Horizon som i ??vrigt inte skiljer sig s??rskilt mycket fr??n f??rut. \n\nUtvecklarna av spelet, Playground Games, har lagt fokus p?? fl??det i spelet vilket m??rks tydligt. Det finns inga startsekvenser, laddningstiderna ??r minimala och v??rlden ??r h??rligt komprimerad vilket g??r att n??sta t??vling alltid finns en kort startstr??cka ifr??n dig. Det h??r skiljer sig ??t en aning fr??n Forza Horizon 3 som hade en mer utspridd spelplats. Fyrans kompakthet bidrar ist??llet till en mer inbjudande upplevelse d??r spelet aldrig st??r still, utan allting flyter ihop fr??n den ena utmaningen till det andra. \n\n??verlag ??r t??vlingarna logiskt indelade. Du har dina t??vlingar p?? landsv??g, p?? skogsv??g och ??ver landskap utan v??g. L??gg d??r till fartkameror, hopp och driftzoner och du har ditt klassiska Horizon-paket. Ut??ver det h??r har utvecklarna ocks?? valt att l??gga in s??rskilda story-uppdrag, en evolution av tidigare Bucket List-uppdrag. Dessa uppdrag erbjuder specifika utmaningar i specifika milj??er. D??r till exempel vissa handlar om att k??ra f??r en driftklubb och sladda runt i s??rskilda superbilar medan andra story-uppdrag till exempel handlar om att k??ra som en stuntf??rare i filminspelningar. Det h??r ??r ett intressant koncept som kommer utvecklas under ??ret. \n\nDet ??r ocks?? med alla de h??r t??vlingarna som Forza Horizon 4 blir intressant. \n\nF??r till skillnad fr??n sina f??reg??ngare har utvecklarna den h??r g??ngen valt att uppdatera spelet under ??rets g??ng. Det kommer inneb??ra inneh??ll i form av nya t??vlingar, nya bilar och nya utmaningar varje vecka. Ett koncept vi sett i s?? m??nga andra spel den senaste tiden.\n\nForza Horizon 4 har dock ett grepp som g??r spelet unikt. \n\nF??r n??r inneh??llet uppdateras f??r??ndras ??ven ??rstiden vilket ??r den enskilt st??rsta nyheten f??r Horizon som spel. \n\nVarje torsdag f??r??ndras klimatet fr??n sommar till h??st, fr??n h??st till vinter och s?? vidare. Ni f??rst??r hur ??rstider fungerar. Dessa ligger sedan p?? m??nadscykler s?? ett ??r i spelv??rlden ??r en m??nad i verklig tid. \n\n![F1](https://i.imgur.com/PrA9A3V.png)\n\nDet h??r ??r n??got som ska bli intressant att f??lja eftersom det ger en anledningar att alltid komma tillbaka till spelv??rlden f??r att jaga nya bel??ningar d?? det kommer finnas event som ??r specifika f??r varje enskild ??rstid. Min f??rhoppning ??r att detta blir inspirerande snarare ??n ??nnu en syssla i v??ra redan pressade spelscheman.\n\nMed ??rstiderna kommer ocks?? olika v??der som p??verkar f??ruts??ttningarna. En regnig bana p?? h??sten k??rs annorlunda fr??n en torr p?? sommaren. H??sten ??r kall och geggig medan sommaren ger varmare v??gbanor f??r h??gre hastigheter. Logiskt liksom. Och det k??nns sm??tt fantastiskt att den nuvarande generationens spel uppfyller s??dant som vi tidigare bara kunde dr??mma om.\n\nForza Horizon 4 utspelar sig i Skottland och landskapet ??r ingenting annat ??n spektakul??rt. H??ga berg, djupa dalar, b??ckar, skogar, stenar, st??der, landsbygd, slott, torp och gruvor. Horizon-serien har hittat hem och det finns s?? mycket detaljer i allt att spelet n??stan ??vertrumfar verkligheten. Det ??r s?? pass personligt och n??ra att det n??stan blir lite jobbigt att f??rst??ra n??gons utem??bler i deras alldeles f??r fina tr??dg??rd. Men jag g??r det ??nd?? f??r jag m??ste samla de samlingsbara objekten som finns g??mda i v??rlden. L??gg till de fyra ??rstiderna p?? allt det h??r och du har fyra olika spelv??rldar i en. \n\nDet ??r ingenting annat ??n magnifikt.\n\nEn annan nyhet f??r serien ??r ocks?? din karakt??r som du kan g??ra personlig med hj??lp av kl??der, accessoarer och emotes. Karakt??ren blir din avatar och jag upplever den vara minst lika mycket i fokus som de bilar du k??r. Det h??r k??nns igen fr??n spel som till exempel Fortnite och det m??rks att Forza Horizon 4 ??r inspirerat av samtiden. \n\nInte mig emot. \n\nFyran har ocks?? ??ndrat uppl??gget med samlingsplatser f??r spelarna. Ist??llet f??r hub-festivaler finns det nu bara en festival i v??rlden och du som spelare bor ist??llet i sm?? s??ta hus som finns utspridda ??ver den brittiska landsbygden, vilket inte ??r en j??ttedum id?? f??r att g??ra spelet mer jordn??ra. \n\nDe h??r nyheterna ger personlighet ??t en serie som tidigare mest handlat om ??verdrivet v??lrenderade bilar p?? vattenblanka landsv??gar. Nu ??r det inbjudande p?? ytterligare s??tt.\n\nRent prestandam??ssigt upplever jag det vara n??got laggigt p?? f??rsta generationens Xbox One. Men jag har spelat med folk som anv??nt PC, Xbox One S och Xbox One X och de s??ger att det inte ??r n??got annat ??n fantastiskt. Och allt eftersom jag tagit mig l??ngre in i spelet s?? m??rker ??ven jag av flytet och den sagolika grafiken. Fyran ??r v??ldigt lik trean rent grafiskt och optimeringen ??r inget annat ??n fenomenal. N??gra dippar i bilduppdateringen kan intr??ffa, men annars fungerar det helt fl??ckfritt.\n\nStyrkan i spelet ??r fortfarande k??nslan av att st??ndigt uppn?? n??gonting d??r hemligheten ligger i den fina balansen mellan krav och bel??ning. Det ??r mer av samma och har du spelat ett tidigare spel s?? vet du exakt vad du har att f??rv??nta dig. \n\nForza Horizon 4 k??nns ocks?? som ett spel som f??r serien i en positiv riktning d??r det fanns en risk allting skulle stagnera. Ist??llet tar Horizon-serien ny kraft och skickar det vidare mot nya h??jder. Jag ser redan fram emot ett femte spel och d?? ??r jag inte ens p?? l??nga v??gar klar med det h??r. Det om n??got ??r ett gott betyg f??r nutidens b??sta arkadracer.\n",
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
                    "title": "Spelkomposit??ren Ben Dalglish d??d. ",
                    "body": "En av de stora komposit??rerna under 8 och 16-bit eran har d??tt.\nBen Dalglish blev 52 ??r och skrev mycket musik f??r bland annat C64, d??ribland The Last Ninja, Switchblade, Krakout och Gauntlet.\n\nhttps://sv.wikipedia.org/wiki/Ben_Daglish\nhttps://youtu.be/hF9mwPUY6b4\n\nhttps://youtu.be/m_Wnt58xeXM\nHttps://youtu.be/OUyGpp6_qA4\n",
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
                    "body": "T??nkte bara tipsa om att Shadow warrior 2 ??r gratis p?? Gog f??r tillf??llet",
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
                    "title": "Importhj??lp",
                    "body": "Det har r??kat bli s?? att jag kommit ??ver n??gra japanska spel, de ??r ju v??ldigt billiga, och s?? l??nge det inte r??r sig om texttunga spel brukar det ju g?? att spela alldeles utm??rkt utanf??r menyerna.\nHar d??rf??r b??rjat snegla lite p?? japanska enheter f??r att kunna spela de h??r spelen optimalt. Har testat lite med konverterare, men de ??r r??tt kinkiga med om de fungerar och kan ge lite mystiska fel ibland eller m??rkliga ??verf??ringar i uppl??sning och hz.\n\nSneglar extra mycket p?? en japansk Gamecube, Mega Drive och Super Famicom, men hur ??r det med att spela s??dana h??r i Sverige? Kan man anv??nda svenska kablar f??r str??m? Har de samma standard f??r bildsladdarna? M??ste jag anv??nda japanska diton med omvandlare p??kopplade?\n\nVill ju kunna spela, men inte finna att jag m??ste f?? tag i en gammal Japan-utvecklat tjock-TV eller r??kar br??nne ner huset f??r att str??momvandlingen blev fel.",
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
                    "title": "New 2ds s??ljes",
                    "body": "Finns det n??got intresse av att ha en 2ds i dagens switch landskap? Jag k??pte maskinen f??rra ??ret och den ??r ytterst sparsamt anv??nd. Vit och orange i f??rg. 32gb minneskort med pokemon sun.\n999kr",
                    "category": "games",
                    "postType": "regular",
                    "createdAt": "2018-10-07T18:43:21.363Z",
                    "updatedAt": "2018-10-07T18:43:21.363Z",
                    "userId": "5bb7b5768fef22001d9028ea",
                    "replies": 0,
                },
                {
                    "id": "5bb889dd8fef22001d902fce",
                    "title": "Super Mario Party s??ljes.",
                    "body": "Endast provspelat.\n\n480:-\n\nSka det skickas st??r jag f??r frakten.\n\nEj intresserad av byten.",
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
                    "title": "Officiella tr??den: K??pa billiga spel",
                    "body": "En av mina favorit tr??dar p?? loading var n??r folk tipsade om billiga spel eller spel som helt enkelt var gratis.\n\nTips om billiga spel blev bannat fr??n k??p och s??lj tr??den s?? t??nkte att jag skapar en f??r bara det h??r ??ndam??let.\n\nRegler: Du f??r tipsa om allt som ??r spelrelaterat, spel, konsoler, handkontroller och liknande.\n\nDet f??r vara s??nkta priser, bra bundles, spel som ??r gratis via tex humble bundle. S?? l??nge Der ??r spel ??r det till??tet. ",
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
                    "title": "Shadow of the Tomb Raider, av Aaron Vesterberg Ringh??g",
                    "body": "# Aaron Vesterberg Ringh??g testar Shadow of the Tomb Raider\n#### Laras os??kerhet kan vara precis vad genren beh??ver.\n\n![Lara Croft](https://images-eds-ssl.xboxlive.com/image?url=8Oaj9Ryq1G1_p3lLnXlsaZgGzAie6Mnu24_PawYuDYIoH77pJ.X5Z.MqQPibUVTcP27a0swKxkIXgb1dv4AtqI4XCXnM0hQ1dfBILJxUZy.Hmu3.2jPm97NlZGozQg9dYtTqOEeewNOxcleTNZm42JMWV3qfcYU3RP838p2RCm6RuHW.i9edsrfwVdyT_fxRIJ4LL0Bw4TPAKQsV9mCZeBucHTGDX9vEiH2ZO_ixlNw-&h=1080&w=1920&format=jpg)\n\nI slutet av maj bj??ds jag in till Square Enix i London f??r att f?? l??gga vantarna p?? ett demo av Shadow of the Tomb Raider. I dryga 40 minuter fick jag sitta med en version av spelet rullandes p?? en Xbox One X f??ljt av en kvart tillsammans med Jill Murray (manusf??rfattare). Vad jag fick uppleva ??r m??h??nda inte representativt f??r ett spel som mycket v??l kan ta tiotals timmar att ta mig igenom, men kanske allra mest en k??nsla av medvetenhet som jag inte sk??dat sedan serien f??rst tog sin plats hos miljontals spelare v??rlden ??ver. K??nslan av os??kerhet hos v??r k??ra protagonist. En k??nsla jag hoppas f?? djupdyka i ??nnu mer n??r spelet v??l sl??pps den 14 september i ??r. \n\nL??t mig f??rklara.\n\nShadow of the Tomb Raider utspelar sig i Sydamerika bland vad som ??r kraftigt influerat av b??de inka- och mayafolkets kulturella milj??arv. Trinity ??r tillbaka som ansikte f??r den giriga organisationen vars fr??msta m??l ??r att ??? ja, vad ??r egentligen Trinitys m??l? ??r de ute efter v??rldsherrav??lde eller st??r de egentligen f??r n??got st??rre? N??got som Lara ??nnu inte lyckats omfamna med sitt st??ndiga fokus p?? att skydda antikens reliker fr??n de onda herrarna i helikoptrar?\n\nFr??gor som dessa ??r, p?? ett n??stan chockerande s??tt, centrala i de 40 minuter jag f??r med Lara. Att g?? in p?? mer narrativa sekvenser ??r d??rf??r n??dv??ndigt f??r att min po??ng ska n?? hela v??gen fram, men f??rst en liten ??verblick ??ver vad jag fick uppleva.\n\nI demot f??r jag ta mig an fyra separata delar. Ett moment d??r mitt uppdrag ??r att utforska Laras nya f??rm??gor p?? slagf??ltet, ett annat d??r jag spionerar p?? en person fr??n Trinity genom Mexicos festivalpyntade sm??gator under de d??das dag, en gravplundring som slutar i en mer scriptad sekvens d??r Lara l??per f??r sitt liv medan allt fallerar omkring henne samt en promenad genom den g??mda staden Paititi.\n\nN??r det kommer till striderna ??r det direkt uppenbart att Shadow of the Tomb Raider inte ??r ett spel d??r det g??r att spela som pacifist. ??ven om jag f??rs??ker springa, alternativt smyga genom en milj?? full av fiender, slutar det tyv??rr ??nd?? alltid p?? samma s??tt. N??gon stackare noterar mig och vips pannkaka ??r jag illa tvungen att ha ihj??l b??de honom och alla hans kollegor. En efter en.\n\nLara har sannerligen blivit den typen av r??skinn hon en g??ng i tiden flydde ifr??n. \n\nF??r oss som spelat de tidigare spelen ??r hennes r??relseschema precis som vi minns, ??ven om Lara nu ges fler m??jligheter och verktyg att anv??nda medan hon tar k??l p?? sina fiender. Hon tar sig an sina offer fr??n tr??dens kronor, fr??n leriga diken och sn??riga buskage som om hon aldrig gjort annat. Och inte en enda g??ng ropar n??gon ???M??rdare!??? efter henne. \n\nBara en s??n sak.\n\nJag kan bara hoppas p?? att det kommer tillf??ra n??gon form av dynamik till ber??ttelsen Eidos Montreal vill f??rmedla i och med den tredje installationen av Tomb Raiders p??nyttf??delse. F??r det finns ??nd?? n??got d??r, det g??r det verkligen. L??t mig ??terkomma till det h??r om en liten stund.\n\nVad g??ller de nya grottorna och pusslen som medf??ljer kan jag egentligen inte s??ga s?? mycket eftersom det omr??de vi fick spela p?? plats var av i princip samma karakt??r som i tidigare installationer. Fysikpussel som l??ses genom att Lara tar sig runt bland v??ggar och ??ver farliga stup f??r att dra i spak A och sedan knuffa stenbumling B, f??r att sedan ??ppna d??rr C. Att Eidos f??rvisso lovar st??rre och mer utmanande pussel ??n n??gonsin tidigare f??r helt enkelt ses som en rej??l morot f??r oss som s??ker oss till genren av just den anledningen. Men i m??ngt och mycket ??r upplevelsen ??nd?? mer av samma. P?? gott och ont.\n\nPaititi som kommer fungera som en central hubb f??r spelet ??r d??remot v??ldigt intressant. En hemlig stad (japp, det finns en till tydligen) fylld av inv??nare som lever sina egna liv, med sina egna behov och m??l, d??r Lara kan ta sig an b??de prim??ra och sekund??ra uppdrag genom att samtala med utvalda inv??nare i staden. Den initiala k??nslan jag f??r n??r jag promenerar runt bland butiker och inv??nare ??r som direkt h??mtad fr??n v??ra mer traditionellt st??pta rollspelsst??der. Jag kan n??stan ana hur Eidos Montreal med sin erfarenhet fr??n framf??r allt Deus Ex-spelen p?? senare ??r har velat ta Tomb Raider vidare ut i ok??nda tr??skmarker. B??de i form av den ??ppna v??rlden, men ??terigen, kanske framf??r allt via ber??ttelsen.\n\nOch det ??r hit jag vill komma.\n\nEn k??nsla av medvetenhet blir pl??tsligt ytterst v??lkommen i en genre som oftast faller platt till f??rm??n f??r den klassiska ???white savior???-tropen som varit alltf??r tydligt etablerad ??nda sedan vi fick se en ung Harrison Ford r??dda antika kulturella arv fr??n ondingar vars enda m??l ??r v??rldsherrav??lde (om inte tidigare). Att Lara Croft, Nathan Drake och n??mnda doktor Jones sedan urminnes tider sj??lva tagit sig r??tten att gr??va upp kulturf??rem??l utan de r??ttm??tiga arvingarnas samtycke ??r ju trots allt ett popul??rkulturellt problem ??ven spelmediet f??tt dras med till denna dag. D??rf??r tycker jag att det k??nns som ett steg i r??tt riktning att f?? ??tminstone en liten hint om vad Lara st??lls inf??r i en av sekvenserna jag fick spela.\n\nMindre spoilers kommer i f??ljande stycke.\n\n![Lara Croft](https://media.playstation.com/is/image/SCEA/shadow-of-the-tomb-raider-screen-08-ps4-us-27apr18?$MediaCarousel_Original$)\n\nI slutet av demot har Lara n??mligen precis lyckats f?? tag i en relik som ska vara avg??rande f??r inte bara folket i den mexikanska byn hon befinner sig i, utan ??ven resten av v??rlden. Hon finner sig dock snabbt tillf??ngatagen av Trinity och under f??ljande meningsutbyte mellan Lara och en av Trinitys ledare, doktor Dominguez, f??r hon snabbt insikten om att saker och ting inte riktigt ??r som hon fr??n b??rjan trodde. Dominguez fr??gar n??mligen om reliken hon fick med sig var allt hon hade f??tt med sig och n??r Lara visar att hon inte har den blekaste aning om vad han pratar om kommer det. Dominguez beordrar snabbt sina mannar med n??stan ??vertydlig desperation i r??sten att sl??ppa henne, innan han beger sig av i en helikopter bara f??r att l??mna en of??rst??ende Lara ensam kvar.\n\nI vad som inte kan vara mer ??n en sekund hinner jag g?? fr??n att se Lara som en stark och m??lmedveten hj??ltinna, till n??got, n??stan sm??rtsamt m??nskligt.\n\nLara, precis som jag, blir m??ll??s.\n\nVad som f??ljer ??r inget mindre ??n en katastrof. Laras handlingar har nu utl??st vad som n??rmast kan likna en apokalyps och innan hon hunnit greppa vad som precis har h??nt, v??ller en flodv??g in ??ver en n??rliggande by som bokstavligen talat g??r under. M??nniskor flyr sina hus och skriker i f??rtvivlan medan deras n??rmaste omkommer i den enorma flodv??gen. I en explosiv sekvens springer Lara f??r sitt liv ??ver rasande husfasader, under elstolpar som faller samman och hamnar till slut kl??ttrandes uppf??r en husv??gg n??r hon ser en liten pojke som h??nger dinglandes ovanf??r en s??ker d??d.\n\nJag kl??ttrar n??rmare och ??r precis p?? v??g att ta mig fram till den skrikande pojken n??r f??stet sl??pper och ??verl??ter pojken till sitt grymma ??de.\n\nBorta. Ingen ???du har misslyckats-sk??rm??? eller omladdning till samma sekvens. Utan bara ???\n\n...borta.\n\nEfter att jag tagit mig upp p?? ett av hustaken som fortfarande st??r upp tr??ffar Lara sin v??n Jonah. H??r intr??ffar nu ett replikskifte som verkligen ger mig f??rhoppningar om att Eidos Montreal har v??gat utveckla Laras karakt??r till en niv?? serien verkligen beh??ver. F??r medan Lara forts??tter ha uppfattningen om att Trinitys enda roll i det stora hela ??r deras  inblandning i hennes fars d??d och allt det hemska som p??g??r, stannar pl??tsligt Jonah upp henne och s??ger n??got som k??nns ??kta och genuint.\n\nHan tar ner Lara p?? jorden. Laras jakt efter Trinity ??r inte l??ngre vad som ??r viktigast. Laras ego tr??der fram som en rak h??ger i k??lvattnet av alla de m??nniskorna som f??tt s??tta livet till p?? grund av hennes framfart.\n\nLaras n??stan totala of??rst??nd inf??r vad hon sj??lv har varit med och skapat blir inte bara effektivt rent narrativt, utan ocks?? ett oerh??rt skickligt hantverk i att ifr??gas??tta protagonistens egen agenda, tillika min som spelare. Att Lara kan b??ra en hel bys ??del??ggelse p?? sina axlar ??ppnar givetvis upp f??r en v??ldigt dynamisk karakt??rsutveckling hos en protagonist som vi l??rt k??nna som en r??ttvis och hedersam karakt??r. Och om det ??r n??got jag vill se mer av s?? ??r det utan tvekan just det h??r.\n\nIfr??gas??ttanden. Inte bara ??ver Laras roll som gravplundrare av reliker, utan ocks?? som person.\n\nOch det, om n??got - vill jag verkligen f?? utforska mer.",
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
                    "title": "??r p?? jakt efter platinum",
                    "body": "Har inte f??tt platinum p?? L??NGE, jag blir tokig. Sn??lla rekommendera ett spel som ger l??tt platinum!!!!!!!!!!!!!!!!!!!!!",
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
                    "body": "# Aleksandar Buntic recenserar Shenmue 1 och 2\n#### Playstation 4\n\n![Shenmue I & II](http://images.pushsquare.com/news/2018/04/soapbox_why_you_should_play_shenmue_i_and_ii_on_ps4/attachment/0/original.jpg)\n\n1998 sl??ppte Sega sin sista spelkonsol. Dreamcast ??r en spelkonsol jag aldrig sj??lv ??gt utan f??tt ta del av genom ett f??tal v??nner. Jag minns s?? v??l f??rsta g??ngen jag fick reda p?? att den ens fanns. Min kompis som hade skilda f??r??ldrar bj??d hem mig till hans pappa f??r f??rsta g??ngen och p?? hans rum stod en underlig maskin. P?? sk??rmen syntes figurer som jag k??nde igen sen tidigare. Sonic och kompani. Det var f??rsta g??ngen jag fick uppleva Sonic Adventure, Crazy Taxi, Samba de Amigo och det skulle ta flera ??r efter den upplevelsen innan jag fick uppleva Dreamcast igen. Det har alltid funnits en spelserie i Dreamcasts bibliotek som jag varit intresserad av.\n\nShenmue.\n\nDet tar inte l??ng tid innan jag f??rst??r hur stort och ambiti??st projekt Shenmue var f??r tiden. Spelet inneh??ller stora ??ppna ytor, m??ngder med inspelade dialoger, unika interaktioner med v??ldetaljerade objekt i v??rlden och ett avancerat stridssystem som tidigare anv??nts i Virtua Fighter-serien. Det ??r ocks?? det spelet som vi har att skylla p?? f??r det f??rbaskade systemet som heter Quick Time Events (okej, det kan funka i vissa typer av spel).  \n\nF??rsta delen i ??ventyret som ??r Shenmue k??nns ganska hoppigt i sin progression. Visst, det finns en struktur d??r, men det dyker upp m??nga stoppklossar p?? v??gen. Spelet b??rjar med att din far blir d??dad av Lan Di, en mystisk man som vill ??t en speciell spegel. Resten av spelet g??r ut p?? att f??rs??ka samla ihop information om Lan Di och hans kompanjoner. \n\nV??rlden ??ppnar upp sig och jag har enbart det som m??l. Inga direkta mark??rer eller vettiga ledtr??dar. Jag vandrar runt i staden och pratar med m??nniskor. St??ller olika fr??gor och f??r olika svar. Ibland kan svaren vara v??sentliga f??r ??ventyret, men ibland ??r svaret s?? fragmenterat att man m??ste fr??ga runt om den nya informationen. Jag tror jag b??rjar f??rst?? vad Metallicas l??t ???Nothing Else Matters??? handlar om . Ni vet: ???So close, no matter how far??????. De olika karakt??rerna som befolkar staden ??r v??ldigt varma. De vill g??rna hj??lpa till och det k??nns verkligen som en gemenskap. Det ??r synd att man inte f??r mer inblick i deras v??rld. Jag hade velat veta mer om ???amerikanen??? (alla amerikaner pratar engelska med japansk brytning) Tom Johnson som s??ljer korvar i sin foodtruck. Eller om Shiro Kurita som ??r besatt av allt som har med milit??ren att g??ra. Shenmue ??r en personlig resa om Ryo Hazukis ??de och jakten p?? h??mnd. \n\nSpelet k??nns som en sm??tt snabbspolad och begr??nsad version av verkliga livet. Den k??nslan f??rst??rks verkligen av hur pass viktig tiden ??r i spelet. Under vissa skeden av spelet var jag tvungen att v??nta p?? att tiden skulle passera ett visst klockslag innan jag kunde ta del av n??sta del av ber??ttelsen. Tiden ??r en otroligt intressant aspekt i spelet som p?? ett s??tt g??r spelet mer levande, men samtidigt g??r det ??ven progressionen mer travande. Det fanns stunder d?? jag k??nde att det var sm??tt frustrerande, d?? jag bara ville f?? forts??tta uppleva ber??ttelsen. Visst, det finns andra saker man kan g??ra i spelet f??r att f?? tiden att g??. Det g??r till exempel att g?? till arkaden och spela gamla klassiska spel som Space Harrier. Det g??r ??ven att g??ra n??gra av de sm?? sidouppdragen. Sedan finns det en hel del samlarobjekt som man kan f??rs??ka samla alla av. F??r mig personligen blev det tillf??llen d?? jag sl??ppte kontrollen och satte mig och gjorde annat medan jag v??ntade p?? att tiden skulle g??. Och det ??r n??got jag egentligen ??r helt okej med. Det f??rst??rde inte min upplevelse av spelet som helhet, men det kr??ver ??nd?? att man ??r villig och har t??lamod. \n\nPengar blir vid ett senare tillf??lle ocks?? en viktig del i spelet. F??r att kunna ta sig vidare m??ste jag jobba ihop pengar genom att transportera l??dor med gaffeltruck. Det ??r ett heltidsjobb d??r man mellan passen f??r en timmes lunch. Denna delen av spelet ??r v??ldigt monoton och tar upp alldeles f??r mycket av spelets slutfas. \n\nN??got som verkligen ??r unikt f??r tiden ??r hur m??nga olika objekt i v??rlden man kan interagera med. Det g??r i stort sett att ??ppna varenda liten lucka eller l??da och i m??nga fall g??r det ??ven att lyfta upp saker som finns i l??dorna f??r en n??rmare titt. N??r man passerar stadens byggnader g??r det ??ven att zooma in p?? gatunummer och skyltar. Oftast ??r denna funktion helt ??verfl??dig f??r att f??ra ber??ttelsen fram??t, men den g??r ??nd?? mycket f??r inlevelsen och trov??rdigheten av v??rlden.\n\nI Shenmue 2 har vi bytt milj?? fr??n den hemtrevliga staden Yokosuka till fr??mmande och sm??tt f??rvirrande distriktet Wan Chai i Hong Kong. Vi ??r inte l??ngre en del av gemenskapen, vi ??r fr??mlingar i ett annat land. Vi har ingenstans att sova och knappt n??gra pengar att leva p??. Det ??r en k??nsla som verkligen formar Shenmue 2 som upplevelse. Det finns s??klart fortfarande v??nliga personer, men de flesta inv??nare man st??ter p?? ??r mer stressade och kr??ver ofta mer i geng??ld. Dessutom ??r det fler g??ng som agerar ??ppet p?? gatan och runt varje h??rn kan man hitta hasardspel i form av ???Lucky Hit???. Skiftet i k??nsla p??verkar hur jag tar mig an spelet. Min st??rsta frustration i spelet kom n??r jag beh??vde samla ihop pengar f??r att f??ra ber??ttelsen fram??t, men f??rlorade g??ng p?? g??ng i Lucky Hit. Jag avskyr slumpen och det ??r det enda det spelet g??r ut p??.\n\n![Shenmue I & II](https://gamingbolt.com/wp-content/uploads/2018/05/shenmue.jpg)\n\nBer??ttelsen i Shenmue 2 ??r mer varierad och har l??ngre interaktioner med m??nga av spelets karakt??rer. En av de f??rsta ??terkommande karakt??rerna i ber??ttelsen ??r Joy, en g??ngmedlem som alltid kommer in p?? sin motorcykel f??r att r??dda Ryo fr??n fara. Hon har mer djup ??n de flesta karakt??rerna i f??rsta spelet. I Hong Kong m??ste Ryo l??ra sig vad som kr??vs f??r att bli en m??stare i Kung Fu. Det skapar en konflikt med Ryos h??mndtankar och det ??r n??got som ofta tas upp av hans Mentor Xiuying Hong. Sj??lva k??rnan i ber??ttelsen ??r dock samma som i f??rsta spelet och interaktionen med stadens inv??nare ??r fortfarande det prim??ra s??ttet att f??ra ber??ttelsen fram??t. \n\nDenna g??ngen ??r dock samtalen med inv??narna inte enbart begr??nsat till att samla information f??r att komma n??rmare Lan Di, utan det g??r ??ven att fr??ga dem om jobb, gambling och var man kan hitta de olika pantbankerna i staden. Det h??r ??r en aspekt som hj??lper till n??r man verkligen beh??ver pengar och det finns n??gra tillf??llen d?? man m??ste samla ihop en viss m??ngd Hong Kong dollar f??r att kunna komma vidare. \n\nTill skillnad fr??n de f?? spel som ??nd?? f??rs??kt efterlikna delar av Shenmue s?? ??r striderna verkligen inte en central del av spelet. F??r mig ??r det otroligt konstigt att spelet har ett avancerat stridssystem n??r det knappt anv??nds i varken det f??rsta spelet eller det andra. Det k??nns lite som att den aspekten inte helt passar in i resten av uppl??gget. Striderna ??r ju helt klart v??lkomnande f??r de ger spelet mer variation, men de ??r ocks?? som b??st okej. Inget jag kommer t??nka p?? n??r jag t??nker p?? Shenmue.\n\n\nDet engelska r??stsk??despeleriet k??nns stelt och saknar inlevelse, vilket i sin tur g??r att de emotionella tonerna i spelet blir sm??tt komiska ist??llet. Karakt??rernas interaktioner l??ter inte trov??rdiga och p??minner mig lite om G??sta Ekmans inlevelse i dokument??rfilmen Pingvinresan. Det ??r sk??nt att det g??r byta fr??n engelska till japanska. F??r mig blir det mycket mer trov??rdigt med ursprungsspr??ket och det blir ocks?? en mer emotionell resa. De tv?? olika spr??kvalen ger helt enkelt tv?? skilda upplevelser av en och samma ber??ttelse. \n\nMusiken ??r otroligt v??lkomponerad och f??rmedlar det visuella och det tematiska v??l. Den ger liv till staden, naturen, kulturen, spelets karakt??rer och f??rst??rker h??ndelserna i ber??ttelsen. Det finns ??ven en bra dynamik mellan olika stilar och ljudbilder. Jag ??lskar min f??rsta interaktion med mataff??ren i Dobuita. Deras jingel kan vara en av de gladaste jag h??rt och det fick mig att m?? bra. Spelets musik kl??ttrar h??gt upp p?? min lista ??ver den b??sta musiken i spel. \n\nDet ??r uppenbart att Shenmue 1 och 2 planerades som ett enda stort spel, men att det inte gick att f?? ihop i tid och det ??r sk??nt att kunna ta del av b??da i ett och samma paket. De flyter ihop med varandra s?? bra. \n\nShenmue 1 och 2 var helt klart unika och ambiti??sa projekt f??r sin tid. Det spelen lyckades ??stadkomma k??nner jag inte riktigt att n??got annat spel eller spelserie lyckats med ??n idag. De ??r l??ngt ifr??n perfekta, men de erbjuder en bredd p?? spelmarknaden som jag uppskattar. Ber??ttelsen, musiken och den visuella stilen tycker jag h??ller ??n idag, medan andra aspekter, s??som styrningen, striderna och r??stsk??despeleriet inte h??ller en lika h??g standard. Det ??r h??r jag hoppas Yu Suzuki f??r??ndrar med uppf??ljaren. F??r mig ??r Shenmue-spelen underbara och en nostalgitripp tillbaka till en era av spel som inte riktigt tillverkas idag, men jag f??rst??r ocks?? att spelen inte ??r f??r alla. Det h??r ??r f??rsta g??ngen jag spelar den h??r spelserien och det h??r paketet fick mig att bli v??ldigt nyfiken p?? att se Yu Suzuki f?? avsluta sin skapelse.\n\n",
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
                    "name": "Coola Anton i Fr??cka Bergen",
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
                    "name": "Aaron Vesterberg Ringh??g",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
    def test_get_other_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bc22315c0c2ba001d07b888",
                    "title": "Tipsa om Youtube-kanaler som ??r v??rda att f??lja (och varf??r!)",
                    "body": "Jag har n??gra n??dv??ndiga stopp p?? Youtube.\n\nDit jag alltid g??r n??r det finns en ny film.\n\nDet ??r dom h??r:\n\n**Good Mythical Morning**\nhttps://www.youtube.com/channel/UC4PooiX37Pld1T8J5SYT-SQ\nGMM har ett nytt avsnitt varje dag klockan 12:00 (och ett extra i Good Mythical More). Det h??r ??r (om du p?? n??got s??tt missat Rhett & Link) en talkshow i miniformat, med fokus p?? olika tester.\n\n**Ashens**\nhttps://www.youtube.com/channel/UCxt9Pvye-9x_AIcb1UtmF1Q\nDet h??r ??r f??r alla er som tycker att Amiga Power hade v??rldens b??sta humor.\n\n**You suck at cooking**\nhttps://www.youtube.com/channel/UCekQr9znsk2vWxBo3YiLq2w\nDet ??r s??llan n??got nytt h??nder p?? YSAC, men n??r det h??nder ??r det alltid det b??sta som h??nt just den veckan.\n\n**Juns Kitchen**\nhttps://www.youtube.com/channel/UCRxAgfYexGLlu1WHGIMUDqw\nMer mat, men s?? l??ngt fr??n YSAC p?? matspektrumet som det g??r att komma. Det h??r ??r imponerande mat som du aldrig kommer att g??ra lika bra sj??lv och v??rldens mest v??luppfostrade katter. \n\n**The Report of the Week**\nhttps://www.youtube.com/channel/UCeR0n8d3ShTn_yrMhpwyE1Q\nSnabbmatsrecensioner med en s?? torr humor att den m??ste ha kostym. Det ??r s?? h??r jag f??rest??ller mig  att Alexander Rehnman skulle vara, om han recenserade snabbmat.\n\n**The Try Guys**\nhttps://www.youtube.com/channel/UCpi8TJfiA4lKGkaXs__YdBA\nP?? n??got s??tt lyckades The Try Guys l??mna Buzzfeed OCH ta med sig varum??rket. Zach ??r naturligtvis b??st.\n\n**Challa**\nhttps://www.youtube.com/channel/UCQa2X1CNCxWF3M6h68g5q6g\nTecknare med humor och sj??lvdistans. Och med ett v??ldigt speciellt s??tt att artikulera sig som jag finner fascinerade att lyssna p??.\n\n**Worth it**\nhttps://www.youtube.com/playlist?list=PL5vtqDuUM1DmXwYYAQcyUwtcalp_SesZD\nEn serie under Buzzfeed d??r Steven och Andrew testar tre versioner av samma matr??tt, men i tre helt olika prisklasser.\n\nNu ??r det din tur - vad f??ljer du?\n\n\n",
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
                    "body": '# UPPDATERING\n\n## K??ra Loadingv??nner! \n\n\nVi vill f??rst b??rja med att tacka er f??r en fantastisk lanseringshelg. Den fantastiskt trevliga och positiva st??mning som r??tt och hur pass v??l allt har fungerat, spartanskt utf??rande till trots, v??rmer v??ra hj??rtan. \n\n\nEr feedback ??r otroligt v??rdefull. Just nu ligger st??rst fokus vid att, i den takt det ??r m??jligt f??r v??r hj??lte Stanislav Izotov, r??tta till diverse fr??getecken och se till att den grundl??ggande upplevelsen blir s?? smidig som m??jligt. P?? l??ng sikt kommer ni att vara en del av hur v??rt community utformas.\n\n\n**Vi vill ta detta tillf??lle i akt att f??rklara varf??r vi valde att lansera nya Loading i ett s?? of??rdigt skick.**\n\n\nDet handlar om tv?? saker:\n\n\nDet viktigaste ??r f??r att vi vill att ni ska k??nna att ni har m??jlighet att direkt p??verka utvecklingen och k??nna er som en del av hela upplevelsen. Att innerst inne veta att alla ni som kommenterat kring saker ocks?? sett till att de har blivit till verklighet. Det g??ller ??ven er som st??ttar oss via Patreon, vilket visar att ni vill se att vi lyckas. Det ger oss en m??jlighet att skapa den m??tesplats och arena vi vill tillsammans med er, ??ven om ni inte uttrycker det i text.\n\n\nDet andra ??r f??r att vi som jobbat med detta projekt i runt fyra m??nader nu och beh??vde en milstolpe f??r att forts??tta str??va fram??t, hitta ny energi och motivation - att helt enkelt f?? en bekr??ftelse p?? att det var m??jligt och att ni fortfarande var med oss!\n\n\nTill sist vill vi ocks?? l??gga vikt vid att n??mna att ni inte ska k??nna er oroliga f??r att era inl??gg ska stryka p?? foten n??r sidan genomg??r sin metamorfos l??ngs v??gen. Trots att sidan ??r som den ??r och att r??tt stora f??r??ndringar kommer att ske, kommer alla era inl??gg finnas kvar tack vare den molnbaserade serverl??sning vi har valt att anv??nda. Det g??r knappt beskriva skillnaden att bygga en s??dan h??r tj??nst idag j??mf??rt med hur det var f??r 10-20 ??r sedan.\n\n\n![alt text](https://i.imgur.com/zSHYABw.png"pixelhj??rta.jpg")\n\n\n__Redaktionen__',
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
                    "body": 'Jag har inte st??tt i bostadsk?? speciellt l??nge tyv??rr, men jag samlar pengar fort och f??rv??ntas kunna k??pa n??got v??ldigt fint i slutet p?? n??sta sommar.\nSom Stockholmare f??r man oftast st?? i k?? i 10-15??r f??r att hitta n??got ordentligt, speciellt i innerstaden. Eller s?? kan man k??pa loss en liten 1a/2a f??r ca 2miljoner.\nMen jag r??kade precis klicka in p?? sidor d??r folk hyr ut sina l??genheter f??r en svinliten avgift (priset f??r 2 n??tter p?? hotell ungef??r) och l??ter en bo d??r under en "obegr??nsad" period.\nVilket ??r sjukt.\n\nN??gon som vet om det r??r sig om helt fejkade sidor, eller har n??gon h??r n??gon som helst erfarenhet? F??r jag ??r v??ldigt f??rvirrad ??ver situationen, vad ??r det jag missat? Alla som st??r utan bostad hade ju klickat hem dessa bost??der p?? 5 sekunder?\n\nH??r ??r ett exempel. Innerstan, en 2:a, 2.300kr i m??naden, obegr??nsad uthyrning.\nhttps://www.hyrenbostad.se/hyresbostad/678999/2-rums-laegenhet-paa-39-m?utm_campaign=Premium&utm_source=Trovit&utm_medium=CPC',
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
                    "body": "Uppf??ljaren till Unbreakable och Split.\n\nPremi??r i b??rjan av n??sta ??r.\n\nhttps://www.youtube.com/watch?v=Q7ztHi9ejp4",
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
                    "title": "Den stora AI tr??den",
                    "body": "Vad har ni f??r tankar kring ??mnet?  \n\nTror ni alls att en maskin kan uppvisa vad som vi menar ??r intelligens? \n\nMedvetande? \n\nLiv? \n\nNi fattar. \n\nSj??lv kommer jag st?? f??rst i robotarnas befrielsefront!",
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
                    "body": "Jag t??nkte bara tipsa er som har problem med att logga in eller problem med att skapa konto att det verkar som att rensa historiken med cachen och allt l??ser det problemet. Iallafall p?? chrome webbl??saren. (:",
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
                    "body": "Orkanen Michael n??rmar sig Florida.\n\nDen ??r n??stan d??r.\n\nDen senaste m??tningen har satt orkanen till en kategori 4, men den ??r n??ra fem och kommer bli starkare hela v??gen in till land. Det ??r med stor sannolikhet den mest intensiva storm som tr??ffat Florida sedan man b??rjade m??tningarna (f??r l??nge sedan).\n\nDet ??r en knapp timme kvar innan Michael n??r land.\n\nDet g??r att hitta lives??ndningar fr??n dom som jagar stormar h??r:\n\nhttps://livestormchasing.com/map",
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
                    "body": "Nya Loading ser lite annorlunda som du kanske har m??rkt =) p?? framsidan kommer du hitta olika kategorier som vi kommer att anv??nda f??r olika sorters material och f??r olika syften:\n\n* UPPDATERING\n\n    Kategorin vi kommer att anv??nda d?? vi annonserar uppdateringar, h??ndelser eller nyheter\n* ??SIKT\n\n    H??r kommer vi l??gga v??ra kr??nikor, f??rtittar, reportage och intervjuer e.t.c\n* SAMTAL\n\n    H??r kommer vi lyfta intressanta och sp??nnande tr??dar fr??n forumet som vi tycker f??rtj??nar lite extra uppm??rksamhet och k??rlek\n* RECENSION\n\n    ??Vi kommer s??klart forts??tta skriva recensioner antingen av spel vi f??tt fr??n utgivare eller som vi k??pt sj??lva.\n* PODCAST\n\n    I Loadings podcastn??tverk ing??r TV-spelspodden och Spelsnack. H??r kan ni ta del av n??gra av Loadingredaktionens tankar kring spel och spelindustrin.\n* STREAM\n\n    Vi kommer forts??tta att streama n??r vi spelar spel via v??ra streamingkanaler som du kan hitta l??ngst ner p?? sidan.\n\n**Forumet**\nSom du snabbt kommer att m??rka har vi bara tv?? forumkategorier p?? nya Loading. Det ??r SPEL-forumet och ANNAT-forumet - Vi vill helt enkelt att s?? m??nga som m??jligt ska delta i de samtal som f??rs och att det som ??r mest aktuellt kommer att vara det som flest vill vara en del av.\n\n**Att Anv??nda Loading p?? mobilen**\nVi har m??rkt att olika webbl??sare och mobiler hanterar nya Loading lite olika. Ett tips ??r att v??lja att visa sidan i datoranpassat l??ge eller liknande funktion som du hittar i inst??llningarna. I ??vrigt ??r nya Loading skapat f??r att fungera lika bra p?? mobilen som p?? datorn.\n\n**Publicera inl??gg:**\nF??r att publicera ett inl??gg skriver du i rutan som vanligt trycker p?? ???skicka??? s?? ??r det klart!\n\nVill du snygga till ditt inl??gg s?? kan vi ber??tta att nya Loading anv??nder Markdown som verktyg f??r att formatera text. Det ??r ett j??ttesmidigt verktyg och du kan hitta en j??ttebra lathund [**H??R**](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)\noch vill du testa och se hur ditt inl??gg ser ut innan du publicerar det kan du g??ra det [**H??R**](https://dillinger.io)\n\nV??lkommen!",
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
                    "name": "Isabell Ryd??n",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
    def test_get_editorials_success(self, mock_requests):
        status_code = 200
        expected_response = {
            "posts": [
                {
                    "id": "5bb797b8066d1b001d528a43",
                    "title": "Bli en del av v??r Patreon",
                    "body": "![Patreon](https://i.imgur.com/lNDGvZd.jpg)\n\n### UPPDATERING 20181208:\n\nHej alla ni tappra underbara Loadare som bidrar till driften, utvecklingen och det redaktionella bakom forumet. Vi vet att vi har varit d??liga p?? att uppdatera v??r Patreon, men det kommer!\nStort tack f??r alla bidrag och STORT TACK f??r att ni ??r ni ??r s?? fina som ni ??r! <3\n\n### ORIGINALPOST:\n\n### K??ra Loadare.\n\nF??r vissa av oss har Loading alltid varit som ett andra hem. En plats som ??r n??got st??rre ??n enbart ett forum p?? internet.\n\nKanske ??r du en av oss?\n\nIdag drivs Loading ideellt av en frist??ende grupp eldsj??lar som beh??ver din hj??lp f??r att t??cka kostnader f??r underh??ll och drift. Med lite fr??n m??nga kan vi lyckas att h??lla liv i forumet samt utveckla och bygga ut det allt eftersom.\nVi tror och hoppas att du som anv??ndare uppskattar forumet och det som redaktionen skapar f??r dig.\n\nVi har uppskattat att det kommer kosta oss ungef??r 1000 kr varje m??nad f??r underh??ll och drift av sidan, vilket vi anser ??r den absolut viktigaste bakgrunden till varf??r vi uppr??ttar en Patreon. Skulle vi f?? in mer pengar ??n det absolut n??dv??ndigaste ser vi detta som en investering i de resurser som kr??vs f??r vidareutveckling av funktioner p?? Loading. Ut??ver det har vi ??ven satt ett m??l f??r att kunna erbjuda redaktionellt material av st??rre kvalit??.\n\nVarma h??lsningar och tack p?? f??rhand f??r din tid.\n\nhttps://www.patreon.com/loadingse/overview\n\n/Loading-redaktionen\n",
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
                    "title": "Ekonomisk rapport f??r 2020 ",
                    "body": "![](https://i.imgur.com/Dr8kWZy.png)\n\n2020 var ett omtumlande ??r f??r v??rlden, och ett sp??nnande ??r f??r Loading. Under ??ret som g??tt har vi inte bara sett m??ngder av recensioner och sp??nnande tr??dar och diskussioner passera f??rbi, utan forumet har ocks?? f??tt sig ett ordentligt lyft. Ut??ver en visuell makeover har v??rt skickliga utvecklingsteam levererat efterl??ngtade funktioner som citering, m??rkt l??ge, ordentliga moderatorverktyg och inb??ddning av YouTube-klipp, samt en och annan buggfix och andra trevliga grejer under huven. Loading kommer s?? klart forts??tta utvecklas under 2021 ocks??.\n\nEftersom vi inte skulle kunna g??ra det vi g??r [utan ert ekonomiska st??d](https://www.patreon.com/loadingse) vill vi tala om exakt vad era pengar g??r till.\n\nUnder 2020 hade Loading int??kter p?? **20??978,08 kr**, f??rdelade s?? h??r:\n\n* **Patreon-inkomster:** 18??571,47 kr\n* **??terbetalning av oavsiktligt hamburgark??p:** 82 kr (mer om detta nedan)\n* **Kvargl??mda Patreon-pengar fr??n innan vi skaffade eget bankkonto:** 2??324,61 kr\n\nV??ra utgifter uppgick till **13??704,20 kr:**\n* **Driftskostnader (serverhyra och dylikt):** 10??281, 20 kr\n* **Bankavgifter:** 1??100 kr\n* **Oavsiktligt hamburgark??p: (en hungrig redaktionsmedlem blippade fel kort i kassan):** 82 kr\n* **Ink??p av kuvert och frim??rken att posta papper som ska skrivas p?? med:** 190 kr\n* **Spelink??p till recensioner:** 2??051 kr\n\nSpelink??pen var f??ljande:\n* **Nioh 2:** 699 kr\n* **What the Golf:** 156 kr\n* **The Last of Us Part II:** 699 kr\n* **Cyberpunk 2077:** 497 kr\n\nDetta resulterade i att vi gick **7??273,88 kr plus.** Eftersom Loading drivs ideellt har vi inga planer p?? att de h??r pengarna ska stoppas i redaktionens fickor eller liknande, utan de ska investeras i att forts??tta driva Loading p?? olika s??tt, till exempel genom ink??p av spel vi inte f??r recensionsexemplar av, eller ink??p av tj??nster som underl??ttar utveckling eller drift av sidan. (Med detta menas d?? mjukvarutj??nster, d?? vi tyv??rr inte har r??d att hyra in professionella utvecklare och betala sk??lig ers??ttning till dem.) En del av pengarna kommer ocks?? anv??ndas f??r att bygga upp en buffert i h??ndelse av of??rutsedda utgifter.\n\nNu blickar vi fram??t mot resten av 2021, som f??rhoppningsvis kommer bli ??nnu ett fantastiskt ??r f??r Loading. Ett forum ??r ingenting utan sina anv??ndare, s?? vi tackar s?? hj??rtligt f??r att ni finns h??r och st??ttar oss.\n\nDet ??r ni som sporrar oss att k??mpa ??nda in i kaklet f??r att g??ra Loading till den b??sta community det kan vara.\n\nNi ??r anledningen att det ??verhuvudtaget finns ett Loading.\n\n??n en g??ng, tack.\n\nV??nliga h??lsningar,\nLoadingredaktionen\n\n![](https://i.imgur.com/6zl9mey.png)\n",
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
                    "title": "Loadingb??ssan 2021 ??? Loading st??djer Musikhj??lpen",
                    "body": "![](https://i.imgur.com/l7xD1oT.png)\n\n# LOADINGB??SSAN 2021\n\nGivmildhetens h??gtid ??r kommen - Julen. Sedan 2008 ??r [Musikhj??lpen](https://sverigesradio.se/artikel/om-musikhjalpen) mer eller mindre bef??st som en riktig jultradition. Genom ??ren har totalt ungef??r 425 miljoner kronor sk??nkts till diverse v??lg??rande ??ndam??l.\n\nDet ??r Norrk??ping som st??r v??rd f??r Musikhj??lpen 2021 och ??rets tema ??r: **F??r en v??rld utan barnarbete.** F??r f??rsta g??ngen p?? 20 ??r har man sett att f??rekomsten av barnarbete har ??kat. Mer information om temat kan du l??sa p?? [Sveriges Radios webbplats](https://sverigesradio.se/artikel/for-en-varld-utan-barnarbete).\n\nSom tidigare ??r har vi sj??lvklart fixat en [**Loadingb??ssa**](https://bossan.musikhjalpen.se/loadingboessan-2021) f??r dig som vill bidra i Loadings namn. F??rra ??ret blev Loadingb??ssan fylld med 550kr. Det b??r vi v??l kunna br??cka?\n\n![](https://i.imgur.com/6zl9mey.png)\n",
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
                    "body": "![](https://i.imgur.com/312v4k9.png)\n# Tack f??r en bra (ny)start!\n\nHej Loading!\n\nH??r kommer en uppdatering kring [v??r Patreon](https://www.patreon.com/loadingse) och en visning p?? hur ert ekonomiska st??d just nu f??rvaltas:\n\nInkomster hittills via v??r Patreon (*betalas ut i mitten av efterkommande m??nad*) uppg??r till totalt **5 288,95 kr**.\n* 13 november: **2 879,70 kr**\n* 14 december: **2 409,25 kr**\n\nUtgifter hittills uppg??r till totalt **3 369 kr**:\n* ??vertagande av dom??nen fr??n Reset Media: **950 kr**\n   (*detta ??r en kostnad som webbhotellet tog ut*)\n* Kostnad f??r databas i oktober: **641,56 kr**\n* Kostnad f??r dom??n i oktober: **55,61 kr**\n* Kostnad f??r databas i november: **717,24 kr**\n* Kostnad f??r dom??n i november: **19,74 kr**\n* Darksiders 3 f??r recension: **549 kr**\n   (*ingen recensionskod fr??n utgivaren*)\n* Katamary Damacy Reroll f??r recension: **179 kr**\n   (*slut p?? recensionskoder hos utgivaren*)\n\nSom ni ser har vi ett ??verskott i v??r kassa. ??verskottet kommer att f??rvaltas av redaktionen f??r behov vid redaktionellt material samt fortsatt buffert f??r driften av Loading. \n\nIdag drivs Loading av eldsj??lar fr??n b??de redaktionen och forumet. Inga pengar kommer att g?? till n??gon form av l??n. Vad vi d??remot kommer att titta p?? ??r scenarion d??r vi kan best??lla ett jobb fr??n en extern part som hj??lper till med vidareutvecklingen av sidan.\n\nTills vidare forts??tter Stanislav att arbeta p?? sidan tillsammans med Terzom, som ni s??kert ocks?? k??nner igen fr??n forumet. \n\nH??r ??r en kort redovisning ??ver vad som gjorts sedan vi lanserade i oktober:\n* Tagit fram textredigerare med m??jlighet att redigera sitt inl??gg med Markdown.\n* M??jlighet att redigera ett redan skapat inl??gg.\n* Uppdaterad styling p?? inl??gg.\n* M??jlighet att ha sin egen profilbild.\n* P??g??ende arbete med olika kontofl??den (*registrering, avregistrering, l??senords??ndring med mera*) \n* Justeringar f??r mobil ??kad l??sbarhet p?? mobil plattform.\n* Allm??nna buggfixar och f??rfiningar.\n\nEn del av v??r vision ??r att ni p?? Loading ska ha m??jligheten att p??verka sidans inneh??ll. D??rf??r undrar vi om ni vill vara med och ge f??rslag p?? vilka spel vi ska k??pa och recensera?\n\nVi vill ocks?? passa p?? att s??ga att vi uppskattar all er feedback som ni har gett oss i [f??rslagstr??den] (https://loading.se/post/5bb790e5066d1b001d528a3a), och vi vill ocks?? att ni medlemmar forts??tter att komma med f??rslag p?? vad som kan f??rb??ttras och vad f??r inneh??ll ni vill se mer av. \n\nOch du, tack f??r ditt st??d, Loading ??r inget utan dig!\n\nF??lj med oss till 2019!\n\nMed varma h??lsningar,\nRedaktionen\n\n![](https://i.imgur.com/RE2YtkV.png)\n\n",
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
                    "body": "![](https://i.imgur.com/QQWY9dI.png)\n\nK??ra Loadare.\nF??r vissa av oss har Loading alltid varit som ett andra hem. En plats som ??r n??got st??rre ??n enbart ett forum p?? internet.\n\nIdag drivs Loading ideellt av en frist??ende grupp eldsj??lar som beh??ver din hj??lp f??r att t??cka kostnader f??r underh??ll och drift. Med lite fr??n m??nga kan vi lyckas att h??lla liv i forumet samt utveckla och bygga ut det allt eftersom.\nVi tror och hoppas att du som anv??ndare uppskattar forumet och det som redaktionen skapar f??r dig.\n\nVi har uppskattat att det kommer kosta oss ungef??r 1000 kr varje m??nad f??r underh??ll och drift av sidan, vilket vi anser ??r den absolut viktigaste bakgrunden till varf??r vi uppr??ttat en Patreon. Skulle vi f?? in mer pengar ??n det absolut n??dv??ndigaste ser vi detta som en investering i Loadings framtid, till exempel genom ink??p av tj??nster och material som l??ter oss f??rb??ttra sidan och det redaktionella inneh??llet.\n\nVarma h??lsningar och tack p?? f??rhand f??r din tid och ditt st??d.\n\nhttps://www.patreon.com/loadingse/overview\n\n/Loading-redaktionen\n\n![](https://i.imgur.com/6zl9mey.png)\n",
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
                    "title": "Nya Loading fyller 1 ??r!",
                    "body": '![](https://i.imgur.com/vQladDr.png)\n\n### **TACK F??R DET H??R ??RET!**\nAtt Loading som fr??n ingenstans st??ngde ned i maj 2018 kom f??r oss alla som en chock. Hur 13 ??r av forumhistoria kunde f??rsvinna s?? pl??tsligt var ledsamt, tragiskt och till och med uppr??rande. Spelforumet var inte bara ??nnu en m??tesplats i spelsverige, under dessa g??ngna ??r hade det blivit en del av m??ngas vardag. Det fanns d??remot de som inte ville acceptera hemsidans ??de, handlingskraftiga individer som var redo att g?? vidare efter detta miss??de.\n\nF??r exakt ett ??r sedan p??b??rjade vi en resa tillsammans med er forumiter. Vi gick hand i hand fr??n gammalt till nytt och lyckades med gemensamt engagemang ??teruppliva v??r gemenskap. Det har sj??lvklart inte alltid varit en l??tt resa, och ingen av oss var nog helt s??kra p?? vart vi var p?? v??g, men nog har det varit roligt ocks??. D??rf??r vill vi sj??lvklart tacka er alla f??r att ni forts??tter att vara med p?? Loading.se i v??tt och torrt. Er som f??ljde med oss fr??n det gamla forumet dit vi ??r idag, er som under det g??ngna ??ret fyllt forumet med intressanta diskussioner och heta debatter.\n\nLoading har alltid handlat om anv??ndarna - ni som varje dag bes??ker forumet, och deltar i hj??rtliga diskussioner om tv-spel och andra ??mnen. Det ??r ni som under alla dessa ??r h??llit Loadings flamma levande, och aldrig har det p??st??endet varit mer sant ??n nu. Idag drivs hemsidan av en frist??ende grupp eldsj??lar och uppr??tth??lls tack vare gener??sa donationer fr??n v??ra anv??ndare. Ett extra stort tack g??r d??rf??r ut till alla er som st??ttar forumet p?? Patreon. Utan era bidrag hade inget av detta varit m??jligt!\n\nL??t oss nu, med ett helt ??r av forumeskapader i backspegeln, blicka fram??t till ytterligare ett framg??ngsrikt och sp??nnande ??r i Loadings tecken! Sk??l!\n\n### **FORUMETS F??RSTA ??R I SIFFROR**\n33433 inl??gg har postats\n446 unika tr??dar har skapats\n219 redaktionella recensioner har publicerats\n1 falsk DO-anm??lning mot forumet har skapats \n\n### **??RETS B??STA TR??DAR**\n\n**[Tr??dlek - En series b??sta spel (The Legend of Zelda)](https://loading.se/post/5d6e5fbb3cc708001eaaf00c) av Jocke Andersson**\nEn av v??rt f??rsta ??rs b??sta tr??dar som lyckades l??ta oss rannsaka v??ra ??sikter p?? ett nyskapande s??tt. Att j??mf??ra alla titlar i en hel spelserie gjorde detta till en underh??llande ??vning i att d??da sina ??lsklingar.\n\n**[The Bullshit Lounge](https://loading.se/post/5bb7aa488fef22001d902643) av Avgrundsvr??l**\nLoadings hj??rta f??rst??s. Med 530 sidor och ??ver 15300 inl??gg finns det ingenting som kan stoppa denna outt??mliga k??lla av skr??ppost. \n\n**[Fikabr??d](https://loading.se/post/5cebf2a48b0a87001db38d7d) av Kiki**\nDen officiella tr??den om allt gott vi k??kar till fikan. \n\n**[Loading blir serie!](https://loading.se/post/5bc0c65911b2c9001d2b3b03) av Avgrundsvr??l**\nTr??den d??r vi under ??ret kunnat illustrera vad som h??nt p?? forumet i form av serier. En underh??llande liten tr??d som beh??ver mer uppm??rksamhet!\n\n**[Presentera det mest fantastiska underskattade spelet](https://loading.se/post/5beb217d033bb1001db3fff2?fbclid=IwAR3i6WREsjvQJqhAOgX5Zrfu6mHfslZ6vQ45N3ODR1yLwFrGRcYz_D1NphU) av Aleksandar Buntic**\nDenna tr??d om underskattade spel blev snabbt fylld med en hel del m??rkliga och sp??nnande titlar som m??nga kanske missat. V??rd att ta en titt p?? om ni vill ha intressanta tips om vad som b??r spelas.\n\n**[Opopul??ra spel??sikter - vilka ??r dina?](https://loading.se/post/5beb217d033bb1001db3fff2?fbclid=IwAR3i6WREsjvQJqhAOgX5Zrfu6mHfslZ6vQ45N3ODR1yLwFrGRcYz_D1NphU) av Alexander Rehnman**\nEn tr??d full med individer som har fel.\n\n**[LLLLINK BBBREAKER!! (Nintendo)](https://loading.se/post/5cd8854de30c54001d547fea) av Shiine**\nBildlekar engagerar alltid p?? ett eller annat s??tt, speciellt om de l??ter en flexa med sin spelsamling p?? kuppen.\n\n**[Charles Martinet h??vdar att Mario inte alls s??ger "So long, gay Bowser!???](https://loading.se/post/5cc7043316aff9001dee48bc) av Alexander Rehnman**\nVi blev ocks?? chockerade n??r vi h??rde det. Fullkomligt orimligt.\n\n**[Varf??r ??r folk s?? r??dda f??r l??gre sv??righetsgrader/tillg??nglighetsalternativ?](https://loading.se/post/5caca66c1c55ff001d4e97df) av Alexander Rehnman**\nKonstn??rliga intentioner och tillg??nglighet st??lls som totala motpunkter i denna diskussion om sv??righetsgrader inom spel. Pajkastning och debatt p?? h??rd niv??.\n\n**[Kulturmarxistisk Gillette-reklam propagerar f??r att m??rda alla m??n!](https://loading.se/post/5c41e1348282b8001d941433) av Avgrundsvr??l**\nPolitik, rakning och PR-trick allt i en och samma tr??d. En helt vanlig strid p?? id??ernas slagf??lt.\n\n**[Duscha p?? morgonen vs duscha p?? kv??llen](https://loading.se/post/5c9baf2a327359001d38683f) av Erik**\nV??r tids kanske viktigaste fr??ga besvarad av forumiterna!\n\n**[K??rlekstr??den!](https://loading.se/post/5c3cb495473055001dadbb3c) av Notorious Gamer**\nTr??den d??r vi delade med oss av v??ra k??rlekseskapader under ??ret som g??tt. Brustna hj??rtan, nyfunnen f??r??lskelse och andra intriger v??ntar i denna dramafyllda forumtr??d.\n\n![](https://i.imgur.com/6zl9mey.png)\n',
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
                    "title": "Styr Loading med din r??st",
                    "body": "Vi har l??nge snickrat p?? l??sningar som tar Loading in i finrummet och blir en naturlig del av din vardag. D??rf??r har vi utvecklat en Google Assistant app d??r du kan prata med Loading.se.\n\nMan kommer ??t den via sin Android-telefon, Google Nest/Home eller Google Assistant appen p?? iPhone. Se till att ha lagt till Svenska bland spr??ken du vill prata p??.\n\nMan b??rjar diskussionen med **Prata med Loading.se**, efter det finns det en rad kommandon man kan leka med.\n\n- Man kan fr??ga efter de **senaste artiklarna**, d?? listar de tre senaste\n- Sedan kan du be den att l??sa den **f??rsta, andra eller tredje** av dessa\n- Ber man den att **s??ka efter** n??got l??ser den upp en bit av det inl??gg som matchade b??st, att s??ka efter *gandalf* ??r alltid en hit\n- Sist men inte minst lanserar vi ??ntligen funktionen att f?? h??ra hur m??nga tr??dar och inl??gg som finns p?? Loading, be bara att f?? h??ra om den **totala statistiken**\n\nAppen vill g??rna h??lla dig kvar i konversationen s?? man kan avsluta genom att inte prata med den p?? ett tag eller helt enkelt s??ga **hejd??** eller **adj??**.\n\nMan kan ocks?? komma direkt till en funktion genom att s??ga **Prata med Loading.se om de senaste nyheterna**.\n\nHoppas ni kommer ha mycket kul genom att prata med Loading.se\n\n[Kolla in appen p?? sidan f??r Google Assistant](https://assistant.google.com/services/a/uid/0000003c159950f9?hl=sv_se)",
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
                    "body": '# UPPDATERING\n\n## K??ra Loadingv??nner! \n\n\nVi vill f??rst b??rja med att tacka er f??r en fantastisk lanseringshelg. Den fantastiskt trevliga och positiva st??mning som r??tt och hur pass v??l allt har fungerat, spartanskt utf??rande till trots, v??rmer v??ra hj??rtan. \n\n\nEr feedback ??r otroligt v??rdefull. Just nu ligger st??rst fokus vid att, i den takt det ??r m??jligt f??r v??r hj??lte Stanislav Izotov, r??tta till diverse fr??getecken och se till att den grundl??ggande upplevelsen blir s?? smidig som m??jligt. P?? l??ng sikt kommer ni att vara en del av hur v??rt community utformas.\n\n\n**Vi vill ta detta tillf??lle i akt att f??rklara varf??r vi valde att lansera nya Loading i ett s?? of??rdigt skick.**\n\n\nDet handlar om tv?? saker:\n\n\nDet viktigaste ??r f??r att vi vill att ni ska k??nna att ni har m??jlighet att direkt p??verka utvecklingen och k??nna er som en del av hela upplevelsen. Att innerst inne veta att alla ni som kommenterat kring saker ocks?? sett till att de har blivit till verklighet. Det g??ller ??ven er som st??ttar oss via Patreon, vilket visar att ni vill se att vi lyckas. Det ger oss en m??jlighet att skapa den m??tesplats och arena vi vill tillsammans med er, ??ven om ni inte uttrycker det i text.\n\n\nDet andra ??r f??r att vi som jobbat med detta projekt i runt fyra m??nader nu och beh??vde en milstolpe f??r att forts??tta str??va fram??t, hitta ny energi och motivation - att helt enkelt f?? en bekr??ftelse p?? att det var m??jligt och att ni fortfarande var med oss!\n\n\nTill sist vill vi ocks?? l??gga vikt vid att n??mna att ni inte ska k??nna er oroliga f??r att era inl??gg ska stryka p?? foten n??r sidan genomg??r sin metamorfos l??ngs v??gen. Trots att sidan ??r som den ??r och att r??tt stora f??r??ndringar kommer att ske, kommer alla era inl??gg finnas kvar tack vare den molnbaserade serverl??sning vi har valt att anv??nda. Det g??r knappt beskriva skillnaden att bygga en s??dan h??r tj??nst idag j??mf??rt med hur det var f??r 10-20 ??r sedan.\n\n\n![alt text](https://i.imgur.com/zSHYABw.png"pixelhj??rta.jpg")\n\n\n__Redaktionen__',
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
                    "title": "T??vling ??? Vinn Dreams till PS4!",
                    "body": "![](https://i.imgur.com/zd2gINa.png)\n\nVi i Loading-redaktionen t??vlar nu ut tre exemplar av Dreams till Playstation 4. T??vlingen g??r ut p?? att du ska beskriva en dr??m som du har haft och som du skulle vilja bygga upp i spelet. Vi kommer sedan att v??lja ut tre lyckliga vinnare som f??r varsitt exemplar.\n\n**S?? h??r g??r du f??r att delta:**\n\nBeskriv en dr??m du har haft och som du skulle vilja bygga upp i spelet.\nSkicka in ditt bidrag till info@loading.se med ??mnesraden ???Dreams t??vling???. P?? s?? s??tt f??r vi din e-postadress s?? vi l??tt kan kontakta dig ifall du vinner. Se till att skriva ditt Loading-namn antingen i ??mnesraden eller i sj??lva meddelandet. \nL??gg upp ditt bidrag i denna tr??d. Det ??r frivilligt, men det uppmuntras!\nH??ll tummarna f??r att du vinner!\n\n\nDu har fram till 10 augusti p?? dig att skicka in ditt bidrag.\n\nLycka till!\n\n![](https://i.imgur.com/6zl9mey.png)\n\n",
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
                    "title": "T??vling: Vinn Mass Effect Legendary Edition till Xbox!",
                    "body": "![](https://i.imgur.com/NHxClYQ.png)\n\nVi i redaktionen har f??tt ett exemplar av Mass Effect: Legendary Edition till Xbox att t??vla ut till en lycklig forumit.\n\nOm du vill f?? chansen att ge dig ut i rymden med Shepard, Garrus och g??nget ??? f??r f??rsta eller femtioelfte g??ngen ??? ??r reglerna enkla:\n\nRita ditt eget rymdskepp och skicka ditt bidrag till info@loading.se (s?? vi har din e-postadress om du vinner) senast **klockan 23.59 svensk tid den 21 juni 2021**. M??rk ditt mail med ???Mass Effect???. Det m??ste inte vara ett rymdskepp som passar in i Mass Effects universum, utan det ??r bara din egen fantasi som s??tter gr??nserna. Posta g??rna bidraget i den h??r tr??den ocks??!\n\nDet b??sta rymdskeppet v??ljs sedan ut av oss i redaktionen.\n\nLycka till!\n\n![](https://i.imgur.com/6zl9mey.png)\n",
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
                    "title": "Vill du recensera Dark Souls Remastered f??r Loading?",
                    "body": "# Recensionsuppdrag: Dark Souls Remastered\n**Format: Nintendo Switch**\n\nHej allihopa! Vi t??nkte att vi skulle testa p?? ett nytt sp??nnande koncept h??r p?? forumet. F??r att bygga vidare p?? v??r h??rliga forumkultur och det som g??r oss unika t??nkte vi testa p?? att dela ut ett recensionsuppdrag till en av v??ra l??sare.\n\nVi vill helt enkelt ge n??got tillbaka till er forumiter som ??r med och bidrar till att Loading ??r det fantastiska forum som vi har idag. \n\nVi tror att det h??r skulle kunna leda till n??gonting v??ldigt sp??nnande. N??gonting som vi inte har gjort f??rut.\n\nVi har f??tt ett recensionsexemplar av Dark Souls Remastered fr??n Bergsala och har f??rst??s haft en dialog med utgivaren om den h??r id??n. \n\nDet kommer givetvis att st??llas samma krav p?? text som n??r vi delar ut ett recensionsuppdrag till den riktiga redaktionen. Samma f??ruts??ttningar, samma krav p?? deadline och texten kommer att beh??va korrl??sas av redaktionen innan vi publicerar (h??r ??r det ocks?? bra att t??nka p?? att du kommer att beh??va skriva under recensionen med ditt riktiga namn).\n\nS?? vad s??ger du? ??r du intresserad av att recensera Dark Souls Remastered f??r Loadings r??kning?\n\nI s??dana fall, skriv en rad om vem du ??r och kanske vilket f??rh??llande du har till serien.\n\nVi beh??ver ha ditt svar senast fredagen den 26/10.\n\nEfter det kommer vi att v??lja ut ett av namnen som har anm??lt sitt intresse.\n\nmed v??nliga h??lsningar, Redaktionen",
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
                    "title": "V??lkommen till Loading",
                    "body": "![V??lkommen till Loading](https://i.imgur.com/KwIAdW7.jpg)\n\n# Loading\n#\n#\n.. har alltid varit en plats som ??r s?? mycket mer ??n ett forum p?? internet. F??r m??nga av oss har Loading varit ett naturligt inslag i vardagen ??nda sedan mitten av 00-talet. En m??tesplats f??r att diskutera allt m??jligt, umg??s eller bara l??sa p?? om de senaste nyheterna i spelbranschen.\n\nN??r Loading f??rsvann i b??rjan av den h??r sommaren skapades ett tomrum. Direkt d??refter samlades redaktionen och p??b??rjade samtalet om den framtid som vi nu ??ntligen skymtar.\n\nN??r vi fick m??jligheten att ta ??ver varum??rket f??r Loading och b??rja om tog vi den, f??r att vi fortfarande tror p?? att det finns ett behov av en s??dan h??r m??tesplats p?? internet.\n\nArbetet startade och loggan och designen f??ddes. Vi fick hj??lp med att bygga upp sidan fr??n grunden. Av det gamla finns ingenting kvar f??rutom dr??mmen och den kan ingen ta ifr??n oss. Vi vill att Loading ska forts??tta vara ett rum f??r inkludering, f??r gemenskap och f??r en v??rdegrund d??r alla har samma r??tt att delta.\n\nV??rt nya Loading kommer att forts??tta utvecklas, men f??r att kunna h??lla dr??mmen vid liv s?? kommer vi alla att vara viktigare ??n n??gonsin f??rr. Reset Media ??r inte l??ngre med i bilden. Loading kommer att drivas av Patreon. Forum kostar och vi kommer att beh??va hj??lpas ??t f??r att skapa det h??r. Vi hoppas att du vill hj??lpa till och bidra. Det beh??vs inte s?? mycket om m??nga ??r med.\n\nVi vill ocks?? passa p?? att s??ga tack f??r att du finns, f??r att det ??r du som driver oss fram??t.\n\nNu s??tter vi ig??ng.\n\n#### V??lkommen!\n\n#\n#\nPatreon: http://loading.se/post/5bb797b8066d1b001d528a43  \nOrdning- och trivselregler: http://loading.se/post/5bb76fb0066d1b001d528a11  \nHur funkar nya Loading: http://loading.se/post/5bb78aba066d1b001d528a30  \nDen stora f??rslagstr??den: http://loading.se/post/5bb790e5066d1b001d528a3a  \n\nMed varma h??lsningar, Redaktionen\n",
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
                    "name": "Aaron Vesterberg Ringh??g",
                    "picture": "b44e7341-421f-48fb-81fc-331acd93ba34.jpg",
                    "role": "user",
                    "createdAt": "2018-10-05T12:53:22.371Z",
                    "status": "active",
                },
                {
                    "id": "5bb751cb066d1b001d5289e0",
                    "name": "Isabell Ryd??n",
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.LoadingApiClient._authenticate")
    @patch("loading_sdk.sync_api.client.requests")
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

    @patch("loading_sdk.sync_api.client.requests")
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
