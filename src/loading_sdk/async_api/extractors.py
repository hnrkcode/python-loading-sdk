import json
import re
from abc import ABC, abstractmethod

import aiohttp
from bs4 import BeautifulSoup
from loading_sdk.settings import BASE_URL, USER_AGENT


class Extractor(ABC):
    async def get_source(self, url: str) -> str:
        headers = {"User-Agent": USER_AGENT}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.text()

    def get_script(self, source: str) -> str:
        soup = BeautifulSoup(source, "html.parser")
        main_script = soup.find(src=re.compile(r"/static/js/main\.[0-9a-zA-Z]+\.js"))

        return main_script["src"][1:]

    def get_chunks(self, source: str) -> list:
        chunk_urls = []

        # Extracts the code with the javascript chunks.
        match = re.search(r"(static/js/).+?(?=\{)(.+?(?=\[)).+(.chunk.js)", source)

        if match:
            # Transform the code into valid JSON so the chunk ids can be stored in a python dict.
            file_name_values = re.sub(r"([0-9]+?(?=:))", r'"\1"', match.group(2))
            chunk_ids = json.loads(file_name_values)

            for key, value in chunk_ids.items():
                chunk_url = f"{BASE_URL}/{match.group(1)}{key}.{value}{match.group(3)}"
                chunk_urls.append(chunk_url)

        return chunk_urls

    @abstractmethod
    async def get_data(self):
        pass


class AboutExtractor(Extractor):
    async def get_data(self):
        about_page_source = await self.get_source(f"{BASE_URL}/om")
        main_script_url = self.get_script(about_page_source)
        main_script_source = await self.get_source(f"{BASE_URL}/{main_script_url}")
        chunk_urls = self.get_chunks(main_script_source)
        about_script_url = chunk_urls[-1]
        about_script_source = await self.get_source(about_script_url)

        match = re.search(
            r"var.e=(.+?)(?=\.map).+a=(.+?)(?=\.map)", about_script_source
        )

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


class SocialsExtractor(Extractor):
    async def get_data(self):
        page_source = await self.get_source(BASE_URL)
        main_script_url = self.get_script(page_source)
        main_script_source = await self.get_source(f"{BASE_URL}/{main_script_url}")

        match = re.findall(
            r"(?:href:\")"
            + r"(https:\/\/|https:\/\/www.(.*?)\..*?\/.*?)"
            + r"(?:\",target:\"_blank\",rel:\"noreferrer noopener\",className:)"
            + r"(?:\"Footer-(?:icon|patreon)\")",
            main_script_source,
        )

        if not match:
            return None

        data = [{"name": social[1], "link": social[0]} for social in match]

        return data


class ExtractorFactory(ABC):
    @abstractmethod
    def get_extractor(self) -> Extractor:
        pass


class AboutExtractorFactory(ExtractorFactory):
    def get_extractor(self) -> Extractor:
        return AboutExtractor()


class SocialsExtractorFactory(ExtractorFactory):
    def get_extractor(self) -> Extractor:
        return SocialsExtractor()


async def extract_data(extractor_name):
    factories = {
        "about": AboutExtractorFactory(),
        "socials": SocialsExtractorFactory(),
    }

    if extractor_name in factories:
        factory = factories[extractor_name]
        extractor = factory.get_extractor()
        data = await extractor.get_data()

        return data

    return None
