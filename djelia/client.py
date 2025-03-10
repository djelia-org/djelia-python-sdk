import os
import json
import requests
from typing import List, Dict, Union, Optional, BinaryIO, Generator
import io

from .constants import (
    BASE_URL, 
    API_KEY_HEADER, 
    ENV_API_KEY, 
    ENDPOINTS, 
    SUPPORTED_LANGUAGES,
    VALID_SPEAKER_IDS,
    DEFAULT_SPEAKER_ID
)

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

        self.api_key = api_key or os.environ.get(ENV_API_KEY)
        if not self.api_key:
            raise AuthenticationError(
                f"API key is required. Provide it as an argument or set the {ENV_API_KEY} environment variable."
            )
        
        self.headers = {
            API_KEY_HEADER: self.api_key
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
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        url = f"{BASE_URL}{ENDPOINTS['supported_languages']}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            self._handle_response_error(response)
            
        return response.json()
    
    def translate(self, text: str, source: str, target: str) -> Dict[str, str]:
        if source not in SUPPORTED_LANGUAGES:
            raise LanguageError(f"Source language '{source}' not supported. Must be one of {SUPPORTED_LANGUAGES.keys()}")
        if target not in SUPPORTED_LANGUAGES:
            raise LanguageError(f"Target language '{target}' not supported. Must be one of {SUPPORTED_LANGUAGES.keys()}")
        
        url = f"{BASE_URL}{ENDPOINTS['translate']}"
        data = {
            "text": text,
            "source": SUPPORTED_LANGUAGES.get(source),
            "target": SUPPORTED_LANGUAGES.get(target)
        }
        headers = {**self.headers, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            self._handle_response_error(response)
            
        return response.json()
    
    def transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False) -> Union[List[Dict], Dict]:
        url = f"{BASE_URL}{ENDPOINTS['transcribe']}"
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
    
    def stream_transcribe(self, audio_file: Union[str, BinaryIO], translate_to_french: bool = False) -> Generator[Dict, None, None]:

        url = f"{BASE_URL}{ENDPOINTS['transcribe_stream']}"
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
    
    def text_to_speech(self, text: str, speaker: int = DEFAULT_SPEAKER_ID, output_file: Optional[str] = None) -> Union[bytes, str]:
        if speaker not in VALID_SPEAKER_IDS:
            raise SpeakerError(f"Speaker ID must be one of {VALID_SPEAKER_IDS}, got {speaker}")
        
        url = f"{BASE_URL}{ENDPOINTS['text_to_speech']}"
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
        


        