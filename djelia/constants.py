from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class EndpointConfig:
    translate: Dict[int, str]
    supported_languages: Dict[int, str]
    transcribe: Dict[int, str]
    transcribe_stream: Dict[int, str]
    text_to_speech: Dict[int, str]


@dataclass(frozen=True)
class ModelsVersionConfig:
    transcription: List[int]
    translate: List[int]
    supported_languages: List[int]
    transcribe_stream: List[int]
    text_to_speech: List[int]


@dataclass(frozen=True)
class DjeliaApiConfig:
    BASE_URL: str
    API_KEY_HEADER: str
    ENV_API_KEY: str
    ENDPOINTS: EndpointConfig
    SUPPORTED_LANGUAGES: Dict[str, str]
    VALID_SPEAKER_IDS: List[int]
    DEFAULT_SPEAKER_ID: int
    MODELS_VERSION: ModelsVersionConfig


endpoints = EndpointConfig(
    translate={1: "/api/v1/models/translate"},
    supported_languages={1: "/api/v1/models/translate/supported-languages"},
    transcribe={
        1: "/api/v1/models/transcribe", 
        2: "/api/v2/models/transcribe"
    },
    transcribe_stream={
        1: "/api/v1/models/transcribe/stream", 
        2: "/api/v2/models/transcribe/stream"
    },
    text_to_speech={1: "/api/v1/models/tts"}
)

models_version = ModelsVersionConfig(
    transcription=[1, 2],
    translate=[1],
    supported_languages=[1],
    transcribe_stream=[1, 2],
    text_to_speech=[1]
)

djelia_config = DjeliaApiConfig(
    BASE_URL="https://djelia.cloud",
    API_KEY_HEADER="x-api-key",
    ENV_API_KEY="DJELIA_API_KEY",
    ENDPOINTS=endpoints,
    SUPPORTED_LANGUAGES={
        "fr": "fra_Latn", 
        "en": "eng_Latn",  
        "bam": "bam_Latn",
    },
    VALID_SPEAKER_IDS=[0, 1, 2, 3, 4],
    DEFAULT_SPEAKER_ID=1,
    MODELS_VERSION=models_version
)