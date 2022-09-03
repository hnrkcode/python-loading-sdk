import json
import re

import aiohttp
from bs4 import BeautifulSoup
from loading_sdk.settings import BASE_URL, USER_AGENT


class AboutPageExtractor:
    async def extract_about_data(self):
        about_page_source = await self._get_source(f"{BASE_URL}/om")
        main_script_url = self._extract_main_script_url(about_page_source)
        main_script_source = await self._get_source(f"{BASE_URL}/{main_script_url}")
        about_script_url = self._get_about_script_url(main_script_source)
        about_script_source = await self._get_source(about_script_url)

        return self._get_about_data(about_script_source)

    async def _get_source(self, url):
        headers = {"User-Agent": USER_AGENT}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.text()

    def _get_about_script_url(self, source_code):
        chunk_urls = []

        # Extracts the code with the javascript chunks.
        match = re.search(r"(static/js/).+?(?=\{)(.+?(?=\[)).+(.chunk.js)", source_code)

        if match:
            # Transform the code into valid JSON so the chunk ids can be stored in a python dict.
            file_name_values = re.sub(r"([0-9]+?(?=:))", r'"\1"', match.group(2))
            chunk_ids = json.loads(file_name_values)

            for key, value in chunk_ids.items():
                chunk_url = f"{BASE_URL}/{match.group(1)}{key}.{value}{match.group(3)}"
                chunk_urls.append(chunk_url)

        return chunk_urls[-1]

    def _get_about_data(self, source_code):
        match = re.search(r"var.e=(.+?)(?=\.map).+a=(.+?)(?=\.map)", source_code)

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

        return {
            "people": json.loads(people),
            "moderators": json.loads(moderators),
        }

    def _extract_main_script_url(self, html):
        soup = BeautifulSoup(html, "html.parser")
        main_script = soup.find(src=re.compile(r"/static/js/main\.[0-9a-zA-Z]+\.js"))

        return main_script["src"][1:]
