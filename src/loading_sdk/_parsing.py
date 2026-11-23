import json
import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag


def main_script_path(source: str) -> str | None:
    soup = BeautifulSoup(source, "html.parser")
    script = soup.find(src=re.compile(r"/static/js/main\.[0-9a-zA-Z]+\.js"))
    if isinstance(script, Tag):
        src = script.get("src")
        if isinstance(src, str):
            return src.removeprefix("/")
    return None


def chunk_urls(source: str, base_url: str) -> list[str]:
    match = re.search(r"(static/js/).+?(?=\{)(.+?(?=\[)).+(.chunk.js)", source)
    if not match:
        return []

    # Quote the numeric chunk IDs to turn the JavaScript object into JSON.
    chunk_ids = json.loads(re.sub(r"([0-9]+?(?=:))", r'"\1"', match.group(2)))
    return [
        f"{base_url}/{match.group(1)}{key}.{value}{match.group(3)}"
        for key, value in chunk_ids.items()
    ]


def legacy_about(about_script_source: str) -> dict | None:
    match = re.search(r"var.e=(.+?)(?=\.map).+a=(.+?)(?=\.map)", about_script_source)

    if not match:
        return None

    people = re.sub(r"(\{|\,)([a-z]+)(\:)", r'\1"\2"\3', match.group(1))
    people = re.sub(r"(.+)(')(.+)(')(.+)", r'\1"\3"\5', people)
    people = people.replace('slags "vuxen p', "slags 'vuxen p")
    people = people.replace('riktigt"-framtid', "riktigt'-framtid")
    people = people.replace("\\n", "")
    people = people.encode("utf-8").decode("unicode_escape")

    moderators = re.sub(r"(\{|\,)([a-z]+)(\:)", r'\1"\2"\3', match.group(2))
    moderators = re.sub(r"(.+)(')(.+)(')(.+)", r'\1"\3"\5', moderators)
    moderators = moderators.replace("\\n", "")
    moderators = moderators.encode("utf-8").decode("unicode_escape")

    data = {
        "people": json.loads(people),
        "moderators": json.loads(moderators),
    }

    return data


def social_links(source: str) -> list[dict[str, str]]:
    links = re.findall(
        r'href:"(https://[^"]+)",target:"_blank",rel:"noreferrer noopener",'
        r'className:"Footer-(?:icon|patreon)"',
        source,
    )
    socials = []
    for link in links:
        host = urlsplit(link).hostname
        if host:
            socials.append(
                {"name": host.removeprefix("www.").split(".")[0], "link": link}
            )
    return socials
