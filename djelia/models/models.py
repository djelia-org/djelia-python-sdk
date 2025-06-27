from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class Language(str, Enum):
    FRENCH = "fra_Latn"
    ENGLISH = "eng_Latn"
    BAMBARA = "bam_Latn"


class Versions(int, Enum):
    v1 = 1
    v2 = 2

    @classmethod
    def latest(cls):
        return max(cls, key=lambda x: x.value)

    @classmethod
    def all_versions(cls):
        return list(cls)

    def __str__(self):
        return f"v{self.value}"


@dataclass
class HttpRequestInfo:
    endpoint: str
    method: str


class DjeliaRequest:
    endpoint_prefix = "https://djelia.cloud/api/v{}/models/"

    get_supported_languages: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "translate/supported-languages", method="GET"
    )
    translate: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "translate", method="POST"
    )

    transcribe: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "transcribe", method="POST"
    )

    transcribe_stream: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "transcribe/stream", method="POST"
    )

    tts: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "tts", method="POST"
    )

    tts_stream: HttpRequestInfo = HttpRequestInfo(
        endpoint=endpoint_prefix + "tts/stream", method="POST"
    )


class TranslationRequest(BaseModel):
    text: str
    source: Language
    target: Language


class TTSRequest(BaseModel):
    text: str
    speaker: int | None = 1


class TTSRequestV2(BaseModel):
    text: str = Field(..., max_length=1000)
    description: str
    chunk_size: float | None = Field(default=1.0, ge=0.1, le=2.0)


class SupportedLanguageSchema(BaseModel):
    code: str
    name: str


class TranslationResponse(BaseModel):
    text: str


class TranscriptionSegment(BaseModel):
    text: str
    start: float
    end: float


class FrenchTranscriptionResponse(BaseModel):
    text: str


class Params:
    file: str = "file"
    translate_to_french: str = "translate_to_french"
    filename: str = "audio_file"


class ErrorsMessage:
    ioerror_save: str = "Failed to save audio file:\n Exception {}"
    ioerror_read: str = "Could not read audio file:\n Exception {}"
    speaker_description_error: str = (
        "Description must contain one of the supported speakers: {}"
    )
    speaker_id_error: str = "Speaker ID must be one of {}, got {}"
    api_key_missing: str = (
        "API key must be provided via parameter or environment variable"
    )
    tts_v1_request_error: str = "TTSRequest required for V1"
    tts_v2_request_error: str = "TTSRequestV2 required for V2"
    tts_streaming_compatibility: str = "Streaming is only available for TTS V2"
