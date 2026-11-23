"""Standalone extractor interfaces retained for existing SDK callers."""

from abc import ABC, abstractmethod

import httpx

from loading_sdk._parsing import chunk_urls, main_script_path
from loading_sdk.settings import BASE_URL, USER_AGENT
from loading_sdk.sync_api.client import LoadingApiClient


class Extractor(ABC):
    def get_source(self, url: str) -> str:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url, headers={"User-Agent": USER_AGENT})
            return response.text

    def get_script(self, source: str) -> str | None:
        return main_script_path(source)

    def get_chunks(self, source: str) -> list[str]:
        return chunk_urls(source, BASE_URL)

    @abstractmethod
    def get_data(self):
        pass


class AboutExtractor(Extractor):
    def get_data(self):
        response = LoadingApiClient().get_about()
        return response["data"]


class SocialsExtractor(Extractor):
    def get_data(self):
        response = LoadingApiClient().get_socials()
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


def extract_data(extractor_name: str):
    factories = {
        "about": AboutExtractorFactory(),
        "socials": SocialsExtractorFactory(),
    }

    if extractor_name in factories:
        factory = factories[extractor_name]
        extractor = factory.get_extractor()
        data = extractor.get_data()

        return data

    return None
