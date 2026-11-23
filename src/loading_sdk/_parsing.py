import json
import re

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
