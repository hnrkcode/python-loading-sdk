"""Run with an isolated interpreter after installing a release distribution."""

import asyncio
import sys
from importlib.metadata import version
from pathlib import Path

import httpx

import loading_sdk
from loading_sdk import AsyncLoadingApiClient, LoadingApiClient


def profile(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET" and request.url.path == "/v1/users/profile"
    return httpx.Response(200, json={"name": "reader"})


async def check_async(expected: dict) -> None:
    async with await AsyncLoadingApiClient(
        transport=httpx.MockTransport(profile)
    ) as client:
        assert await client.get_profile() == expected


if __name__ == "__main__":
    assert Path(loading_sdk.__file__).resolve().is_relative_to(Path(sys.prefix))
    assert version("python-loading-sdk") == sys.argv[1]
    expected = {"code": 200, "message": "OK", "data": {"name": "reader"}}
    with LoadingApiClient(transport=httpx.MockTransport(profile)) as client:
        assert client.get_profile() == expected
    asyncio.run(check_async(expected))
