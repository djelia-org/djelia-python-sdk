from typing import Union

import aiohttp
import requests
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_random_exponential)

from djelia.config.settings import Settings
from djelia.src.auth import Auth
from djelia.src.services import (TTS, AsyncTranscription, AsyncTranslation,
                                 AsyncTTS, Transcription, Translation)
from djelia.utils.errors import api_exception, general_exception


class Djelia:
    def __init__(
        self, api_key: Union[str, None] = None, base_url: Union[str, None] = None
    ):
        self.settings = None
        if base_url is None:
            self.settings = Settings()
            self.base_url = self.settings.base_url
        else:
            self.base_url = self.base_url

        if api_key is None:
            self.settings = Settings()
            self.auth = Auth(self.settings.djelia_api_key)
        else:
            self.auth = Auth(api_key=api_key)

        self.translation = Translation(self)
        self.transcription = Transcription(self)
        self.tts = TTS(self)

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_random_exponential(multiplier=1, max=40),
        stop=stop_after_attempt(3),
    )
    def _make_request(self, method: str, endpoint: str, **kwargs):
        headers = self.auth.get_headers()

        if "params" in kwargs:
            params = kwargs["params"]
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        try:
            response = requests.request(method, endpoint, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            raise api_exception(code=e.response.status_code, error=e)
        except requests.exceptions.RequestException as e:
            raise general_exception(error=e)


class DjeliaAsync:
    def __init__(
        self, api_key: Union[str, None] = None, base_url: Union[str, None] = None
    ):
        self.settings = None
        if base_url is None:
            self.settings = Settings()
            self.base_url = self.settings.base_url
        else:
            self.base_url = self.base_url

        if api_key is None:
            self.settings = Settings()
            self.auth = Auth(self.settings.djelia_api_key)
        else:
            self.auth = Auth(api_key=api_key)

        self.translation = AsyncTranslation(self)
        self.transcription = AsyncTranscription(self)
        self.tts = AsyncTTS(self)
        self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @property
    def session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_random_exponential(multiplier=1, max=40),
        stop=stop_after_attempt(3),
    )
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        headers = self.auth.get_headers()

        if "params" in kwargs:
            params = kwargs["params"]
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        async with self.session.request(
            method, endpoint, headers=headers, **kwargs
        ) as response:
            try:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()

                if "application/json" in content_type:
                    return await response.json()
                else:
                    return await response.read()

            except aiohttp.ClientResponseError as e:
                raise api_exception(code=e.status, error=e)
            except aiohttp.ClientError as e:
                raise general_exception(error=e)

    async def _make_streaming_request(self, method: str, endpoint: str, **kwargs):
        headers = self.auth.get_headers()

        if "params" in kwargs:
            params = kwargs["params"]
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        response = await self.session.request(
            method, endpoint, headers=headers, **kwargs
        )
        try:
            response.raise_for_status()
            return response
        except (aiohttp.ClientResponseError, aiohttp.ClientError) as e:
            await response.close()
            if isinstance(e, aiohttp.ClientResponseError):
                raise api_exception(code=e.status, error=e)
            else:
                raise general_exception(error=e)
