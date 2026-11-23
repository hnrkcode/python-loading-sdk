"""Standalone extractor interfaces retained for existing SDK callers."""

from abc import ABC, abstractmethod

import httpx

from loading_sdk._parsing import chunk_urls, main_script_path
from loading_sdk.async_api.client import AsyncLoadingApiClient
from loading_sdk.settings import BASE_URL, USER_AGENT


class Extractor(ABC):
    async def get_source(self, url: str) -> str:
        async with httpx.AsyncClient(follow_redirects=True, timeout=300) as client:
            response = await client.get(url, headers={"User-Agent": USER_AGENT})
            return response.text

    def get_script(self, source: str) -> str | None:
        return main_script_path(source)

    def get_chunks(self, source: str) -> list[str]:
        return chunk_urls(source, BASE_URL)

    @abstractmethod
    async def get_data(self):
        pass


class AboutExtractor(Extractor):
    async def get_data(self):
        response = await AsyncLoadingApiClient().get_about()
        return response["data"]


class SocialsExtractor(Extractor):
    async def get_data(self):
        response = await AsyncLoadingApiClient().get_socials()
        return response["data"]


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


async def extract_data(extractor_name: str):
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
