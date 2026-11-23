"""Shared SDK operations yield HTTP requests and consume buffered responses.

The sync and async clients drive these operations with their respective HTTPX clients.
"""

from collections.abc import Generator
from typing import Any, TypeVar

import httpx

from loading_sdk import _parsing, settings

T = TypeVar("T")
Operation = Generator[httpx.Request, httpx.Response, T]
Result = dict[str, Any]


def request(
    method: str,
    path: str,
    *,
    data: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    authenticated: bool = False,
) -> httpx.Request:
    return httpx.Request(
        method,
        f"{settings.API_URL}/{settings.API_VERSION}/{path}",
        headers={"User-Agent": settings.USER_AGENT, **(headers or {})},
        data=data,
        extensions={"sdk_auth": authenticated},
    )


def web_request(path: str) -> httpx.Request:
    return httpx.Request(
        "GET",
        f"{settings.BASE_URL}/{path}",
        headers={"User-Agent": settings.USER_AGENT},
    )


def result(data: Any, message: str = "OK", code: int = 200) -> Result:
    return {"code": code, "message": message, "data": data}


def parsed(response: httpx.Response, message: str = "OK", status: int = 200) -> Result:
    data = response.json()
    return result(data, message, status) if response.status_code == status else data


def authenticate(email: str, password: str) -> Operation[Result]:
    login = request("POST", "auth/login", data={"email": email, "password": password})
    login.extensions["sdk_login"] = True
    response = yield login
    if response.status_code == 200:
        return {"code": 200, "cookies": login.extensions["sdk_cookies"]}
    return response.json()


def get_profile() -> Operation[Result]:
    return parsed((yield request("GET", "users/profile", authenticated=True)))


def search(query: str) -> Operation[Result]:
    response = yield request(
        "POST",
        "search/",
        data={"query": query},
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
    )
    data = response.json()
    if response.status_code != 200:
        return data
    return result(data, "OK" if data["posts"] else "No results")


def missing(field: str, code: int) -> Result:
    return {"code": code, "message": f'"{field}" is not allowed to be empty'}


def get_post(post_id: str) -> Operation[Result]:
    if not post_id:
        return missing("post_id", 404)
    return parsed((yield request("GET", f"posts/{post_id}")))


def page_count(replies: int) -> int:
    return max(1, (replies + settings.POSTS_PER_PAGE - 1) // settings.POSTS_PER_PAGE)


def page_error(message: str, code: int) -> Result:
    return result({"posts": [], "users": []}, message, code)


def get_thread(thread_id: str, page: int | None = None) -> Operation[Result]:
    if not thread_id:
        return missing("thread_id", 404)
    headers = {"page": str(page)} if page and page > 1 else {}
    response = yield request("GET", f"posts/{thread_id}", headers=headers)
    data = response.json()
    if response.status_code != 200:
        return data
    first = data["posts"][-1]
    if "title" not in first:
        return {"code": 200, "message": "Exists, but was not a thread id"}
    if page and page < 1:
        return page_error("Page number too low", 200)
    if page and page > page_count(first["replies"]):
        return page_error("Page number too high", 200)
    return result(data)


def category_headers(
    category: str,
    page: int | None,
    post_type: str | None = None,
    sort: str | None = None,
) -> dict[str, str]:
    headers = {category: category}
    if page and page > 1:
        headers["page"] = str(page)
    if category == "texts":
        headers["post-type"] = (
            post_type if post_type in settings.EDITORIAL_POST_TYPES else "neRegular"
        )
        if sort and sort in settings.EDITORIAL_SORT:
            headers["sort"] = sort
    return headers


def category_page(
    category: str,
    page: int | None,
    post_type: str | None = None,
    sort: str | None = None,
) -> Operation[Result]:
    if page and page < 1:
        return page_error("Page number too low", 404)
    response = yield request(
        "GET", "posts/", headers=category_headers(category, page, post_type, sort)
    )
    data = response.json()
    if "posts" not in data:
        return data
    if not data["posts"]:
        return result(data, "Page number too high", 404)
    return result(data)


def create_post(thread_id: str, message: str) -> Operation[Result]:
    if not thread_id:
        return missing("thread_id", 400)
    response = yield request(
        "POST", f"posts/{thread_id}", data={"body": message}, authenticated=True
    )
    return parsed(response, "Post created", 201)


def edit_post(post_id: str, message: str) -> Operation[Result]:
    if not message:
        return missing("message", 400)
    response = yield request(
        "PATCH", f"posts/{post_id}", data={"body": message}, authenticated=True
    )
    return parsed(response, "Post updated")


def create_thread(
    title: str, message: str, category_name: str, post_type: str | None
) -> Operation[Result]:
    if category_name not in ("games", "other"):
        return {"code": 400, "message": "Invalid forum category"}
    if post_type and post_type not in settings.EDITORIAL_POST_TYPES:
        return {"code": 400, "message": "Invalid post_type"}
    response = yield request(
        "POST",
        "posts/",
        authenticated=True,
        data={
            "category": category_name,
            "postType": post_type or "regular",
            "title": title,
            "body": message,
        },
    )
    return parsed(response, "Thread created", 201)


def edit_thread(thread_id: str, message: str) -> Operation[Result]:
    response = yield from edit_post(thread_id, message)
    if response["code"] == 200:
        response["message"] = "Thread updated"
    return response


def main_script(page: str) -> Operation[str | None]:
    html = yield web_request(page)
    path = _parsing.main_script_path(html.text)
    if path is None:
        return None
    script = yield web_request(path)
    return script.text


def get_about() -> Operation[Result]:
    response = yield request("GET", "editorial/")
    if response.status_code == 200:
        data = response.json()
        return result({"people": data["editorials"], "moderators": data["moderators"]})
    if response.status_code == 404:
        # Older deployments embed the staff lists in a JavaScript chunk.
        script = yield from main_script("om")
        chunks = _parsing.chunk_urls(script or "", settings.BASE_URL)
        if chunks:
            chunk = yield httpx.Request(
                "GET", chunks[-1], headers={"User-Agent": settings.USER_AGENT}
            )
            staff = _parsing.legacy_about(chunk.text)
            if staff:
                return result(staff)
    return result(None, "No data found", 404)


def get_socials() -> Operation[Result]:
    script = yield from main_script("")
    links = _parsing.social_links(script or "")
    return result(links) if links else result(None, "No results found", 404)


def get_total_thread_pages(thread_id: str) -> Operation[int | Result]:
    response = yield from get_thread(thread_id)
    if response["code"] != 200 or "data" not in response:
        return response
    return page_count(response["data"]["posts"][-1]["replies"])


def get_total_category_pages(category: str) -> Operation[Result]:
    if category not in settings.FORUM_CATEGORIES:
        return result(None, "Invalid category", 404)
    lower, upper, page = 0, None, 1
    while upper is None or upper - lower > 1:
        headers = category_headers(category, page)
        headers["page"] = str(page)
        response = yield request("GET", "posts/", headers=headers)
        data = response.json()
        if "posts" not in data:
            return data
        if data["posts"]:
            lower = page
        else:
            upper = page
        page = page * 2 if upper is None else (lower + upper) // 2
    return result({"total_pages": lower})
