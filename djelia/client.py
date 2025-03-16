import os
import json
import requests
from typing import List, Dict, Union, Optional, BinaryIO, Generator, AsyncGenerator

import aiohttp
from .constants import djelia_config

from .exceptions import (
    DjeliaError, 
    AuthenticationError, 
    ValidationError,
    APIError,
    LanguageError,
    SpeakerError,
    AudioFormatError
)


class Djelia:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get(djelia_config.ENV_API_KEY)
        if not self.api_key:
            raise AuthenticationError(
                f"API key is required. Provide it as an argument or set the {djelia_config.ENV_API_KEY} environment variable."
            )
        
        self.headers = {
            djelia_config.API_KEY_HEADER: self.api_key
        }
    

    def _handle_response_error(self, response: requests.Response) -> None:
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key or unauthorized access")
        
        elif response.status_code == 422:
            try:
                error_detail = response.json().get("detail", "Validation failed")
                raise ValidationError(f"Validation error: {error_detail}")
            except (json.JSONDecodeError, AttributeError):
                raise ValidationError("Validation error")
            
        elif response.status_code != 200:
            try:
                error_msg = response.json().get("detail", response.text or "Unknown error")
            except (json.JSONDecodeError, AttributeError):
                error_msg = response.text or "Unknown error"
            raise APIError(response.status_code, error_msg)
    

    def get_supported_languages(self, version: int = 1) -> List[Dict[str, str]]:
        if version not in djelia_config.MODELS_VERSION.supported_languages:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.supported_languages}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.supported_languages.get(version)}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            self._handle_response_error(response)

        return response.json()
    

    def translate(self, text: str, source: str, target: str, version: int = 1) -> Dict[str, str]:
        if version not in djelia_config.MODELS_VERSION.translate:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.translate}")

        if source not in djelia_config.SUPPORTED_LANGUAGES:
            raise LanguageError(f"Source language '{source}' not supported. Must be one of {djelia_config.SUPPORTED_LANGUAGES.keys()}")
        
        if target not in djelia_config.SUPPORTED_LANGUAGES:
            raise LanguageError(f"Target language '{target}' not supported. Must be one of {djelia_config.SUPPORTED_LANGUAGES.keys()}")
        
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.translate.get(version)}"
        data = {
            "text": text,
            "source": djelia_config.SUPPORTED_LANGUAGES.get(source),
            "target": djelia_config.SUPPORTED_LANGUAGES.get(target)
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            self._handle_response_error(response)
            
        return response.json()
    

    def transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False, version: int = 2) -> Union[List[Dict], Dict]:
        if version not in djelia_config.MODELS_VERSION.transcription:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.transcription}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.transcribe.get(version)}"
        params = {"translate_to_french": translate_to_french}
        
        try:
            if isinstance(audio_file, str):
                with open(audio_file, 'rb') as f:
                    files = {"file": f}
                    response = requests.post(url, headers=self.headers, params=params, files=files)
            else:
                files = {"file": audio_file}
                response = requests.post(url, headers=self.headers, params=params, files=files)
        except IOError as e:
            raise IOError(f"Could not read audio file: {str(e)}")
        
        if response.status_code != 200:
            self._handle_response_error(response)
            
        return response.json()
    

    def stream_transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False, version: int = 1) -> Generator[Dict, None, None]:
        if version not in djelia_config.MODELS_VERSION.transcribe_stream:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.transcribe_stream}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.transcribe_stream.get(version)}"
        params = {"translate_to_french": translate_to_french}
        
        try:
            if isinstance(audio_file, str):
                with open(audio_file, 'rb') as f:
                    files = {"file": f}
                    response = requests.post(url, headers=self.headers, params=params, files=files, stream=True)
            else:
                files = {"file": audio_file}
                response = requests.post(url, headers=self.headers, params=params, files=files, stream=True)
        except IOError as e:
            raise IOError(f"Could not read audio file: {str(e)}")
        
        if response.status_code != 200:
            self._handle_response_error(response)
        
        for line in response.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                except json.JSONDecodeError:
                    continue
    

    def text_to_speech(self, text: str, speaker: int = djelia_config.DEFAULT_SPEAKER_ID, output_file: Optional[str] = None, version: int = 1) -> Union[bytes, str]:
        if version not in djelia_config.MODELS_VERSION.text_to_speech:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.text_to_speech}")
            
        if speaker not in djelia_config.VALID_SPEAKER_IDS:
            raise SpeakerError(f"Speaker ID must be one of {djelia_config.VALID_SPEAKER_IDS}, got {speaker}")
        
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.text_to_speech.get(version)}"
        data = {
            "text": text,
            "speaker": speaker
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            self._handle_response_error(response)
        
        if output_file:
            try:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return output_file
            except IOError as e:
                raise IOError(f"Failed to save audio file: {str(e)}")
        else:
            return response.content
        


class AsyncDjelia:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get(djelia_config.ENV_API_KEY)
        if not self.api_key:
            raise AuthenticationError(
                f"API key is required. Provide it as an argument or set the {djelia_config.ENV_API_KEY} environment variable."
            )
        
        self.headers = {
            djelia_config.API_KEY_HEADER: self.api_key
        }
        self._session = None
    
    @property
    def session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _handle_response_error(self, response: aiohttp.ClientResponse) -> None:
        if response.status == 401:
            raise AuthenticationError("Invalid API key or unauthorized access")
        elif response.status == 422:
            try:
                error_data = await response.json()
                error_detail = error_data.get("detail", "Validation failed")
                raise ValidationError(f"Validation error: {error_detail}")
            except (json.JSONDecodeError, aiohttp.ContentTypeError):
                raise ValidationError("Validation error")
        elif response.status != 200:
            try:
                error_data = await response.json()
                error_msg = error_data.get("detail", await response.text() or "Unknown error")
            except (json.JSONDecodeError, aiohttp.ContentTypeError):
                error_msg = await response.text() or "Unknown error"
            raise APIError(response.status, error_msg)
    

    async def get_supported_languages(self, version: int = 1) -> List[Dict[str, str]]:
        if version not in djelia_config.MODELS_VERSION.supported_languages:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.supported_languages}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.supported_languages.get(version)}"
        
        async with self.session.get(url, headers=self.headers) as response:
            if response.status != 200:
                await self._handle_response_error(response)
                
            return await response.json()
    

    async def translate(self, text: str, source: str, target: str, version: int = 1) -> Dict[str, str]:
        if version not in djelia_config.MODELS_VERSION.translate:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.translate}")
            
        if source not in djelia_config.SUPPORTED_LANGUAGES:
            raise LanguageError(f"Source language '{source}' not supported. Must be one of {djelia_config.SUPPORTED_LANGUAGES.keys()}")
        if target not in djelia_config.SUPPORTED_LANGUAGES:
            raise LanguageError(f"Target language '{target}' not supported. Must be one of {djelia_config.SUPPORTED_LANGUAGES.keys()}")
        
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.translate.get(version)}"
        data = {
            "text": text,
            "source": djelia_config.SUPPORTED_LANGUAGES.get(source),
            "target": djelia_config.SUPPORTED_LANGUAGES.get(target)
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                await self._handle_response_error(response)
                
            return await response.json()
    

    async def transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False, version: int = 1) -> Union[List[Dict], Dict]:
        if version not in djelia_config.MODELS_VERSION.transcription:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.transcription}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.transcribe.get(version)}"
        params = {"translate_to_french": str(translate_to_french).lower() }
        
        try:
            if isinstance(audio_file, str):
                with open(audio_file, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f.read(), filename=os.path.basename(audio_file))
                    
                    async with self.session.post(url, headers=self.headers, params=params, data=data) as response:
                        if response.status != 200:
                            await self._handle_response_error(response)
                            
                        return await response.json()
            else:
                data = aiohttp.FormData()
                data.add_field('file', audio_file.read(), filename='audio_file')
                
                async with self.session.post(url, headers=self.headers, params=params, data=data) as response:
                    if response.status != 200:
                        await self._handle_response_error(response)
                        
                    return await response.json()
        except IOError as e:
            raise IOError(f"Could not read audio file: {str(e)}")
    

    async def stream_transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False, version: int = 1) -> AsyncGenerator[Dict, None]:
        if version not in djelia_config.MODELS_VERSION.transcribe_stream:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.transcribe_stream}")
            
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.transcribe_stream.get(version)}"
        params = {"translate_to_french": str(translate_to_french).lower() }
        
        try:
            if isinstance(audio_file, str):
                with open(audio_file, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f.read(), filename=os.path.basename(audio_file))
                    
                    async with self.session.post(url, headers=self.headers, params=params, data=data) as response:
                        if response.status != 200:
                            await self._handle_response_error(response)
                        
                        async for line in response.content:
                            line = line.strip()
                            if line:
                                try:
                                    yield json.loads(line.decode('utf-8'))
                                except json.JSONDecodeError:
                                    continue
            else:
                data = aiohttp.FormData()
                data.add_field('file', audio_file.read(), filename='audio_file')
                
                async with self.session.post(url, headers=self.headers, params=params, data=data) as response:
                    if response.status != 200:
                        await self._handle_response_error(response)
                    
                    async for line in response.content:
                        line = line.strip()
                        if line:
                            try:
                                yield json.loads(line.decode('utf-8'))
                            except json.JSONDecodeError:
                                continue
        except IOError as e:
            raise IOError(f"Could not read audio file: {str(e)}")
    

    async def text_to_speech(self, text: str, speaker: int = djelia_config.DEFAULT_SPEAKER_ID, output_file: Optional[str] = None, version: int = 1) -> Union[bytes, str]:
        if version not in djelia_config.MODELS_VERSION.text_to_speech:
            raise ValidationError(f"Version must be one of {djelia_config.MODELS_VERSION.text_to_speech}")
            
        if speaker not in djelia_config.VALID_SPEAKER_IDS:
            raise SpeakerError(f"Speaker ID must be one of {djelia_config.VALID_SPEAKER_IDS}, got {speaker}")
        
        url = f"{djelia_config.BASE_URL}{djelia_config.ENDPOINTS.text_to_speech.get(version)}"
        data = {
            "text": text,
            "speaker": speaker
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        
        async with self.session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                await self._handle_response_error(response)
            
            content = await response.read()
            
            if output_file:
                try:
                    with open(output_file, 'wb') as f:
                        f.write(content)
                    return output_file
                except IOError as e:
                    raise IOError(f"Failed to save audio file: {str(e)}")
            else:
                return content