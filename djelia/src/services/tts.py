import warnings
from collections.abc import AsyncGenerator, Generator

from djelia.models import (DjeliaRequest, ErrorsMessage, TTSRequest,
                           TTSRequestV2, Versions)
from djelia.utils.exceptions import SpeakerError


def _build_request(
    client,
    version: Versions,
    input: str,
    voice: int | None,
    description: str | None,
    chunk_size: float,
) -> TTSRequest | TTSRequestV2:
    """Build and validate the underlying TTS request for the given version."""
    if version == Versions.v1:
        if voice is None:
            voice = client.settings.default_speaker_id
        request = TTSRequest(text=input, speaker=voice)
        if request.speaker not in client.settings.valid_speaker_ids:
            raise SpeakerError(
                ErrorsMessage.speaker_id_error.format(
                    client.settings.valid_speaker_ids, request.speaker
                )
            )
        return request

    if description is None:
        raise ValueError(ErrorsMessage.tts_v2_description_required)
    request = TTSRequestV2(text=input, description=description, chunk_size=chunk_size)
    speaker_found = any(
        speaker.lower() in request.description.lower()
        for speaker in client.settings.valid_tts_v2_speakers
    )
    if not speaker_found:
        raise SpeakerError(
            ErrorsMessage.speaker_description_error.format(
                client.settings.valid_tts_v2_speakers
            )
        )
    return request


class Speech:
    """OpenAI-style text-to-speech resource: ``client.audio.speech``."""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        *,
        input: str,
        voice: int | None = None,
        description: str | None = None,
        model: Versions | int | str = Versions.v1,
        chunk_size: float = 1.0,
        stream: bool = False,
        output_file: str | None = None,
    ) -> bytes | str | Generator:
        version = Versions.from_value(model)
        request = _build_request(
            self.client, version, input, voice, description, chunk_size
        )

        if stream:
            if version == Versions.v1:
                raise ValueError(ErrorsMessage.tts_streaming_compatibility)
            return self._stream(request, output_file, version)

        response = self.client._make_request(
            method=DjeliaRequest.tts.method,
            endpoint=DjeliaRequest.tts.endpoint.format(version.value),
            json=request.dict(),
        )
        if output_file:
            try:
                with open(output_file, "wb") as f:
                    f.write(response.content)
                return output_file
            except OSError as e:
                raise OSError(ErrorsMessage.ioerror_save.format(str(e)))
        return response.content

    def _stream(
        self,
        request: TTSRequestV2,
        output_file: str | None,
        version: Versions,
    ) -> Generator[bytes, None, None]:
        response = self.client._make_request(
            method=DjeliaRequest.tts_stream.method,
            endpoint=DjeliaRequest.tts_stream.endpoint.format(version.value),
            json=request.dict(),
            stream=True,
        )

        audio_chunks = []
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                audio_chunks.append(chunk)
                yield chunk

        if output_file:
            try:
                with open(output_file, "wb") as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
            except OSError as e:
                raise OSError(ErrorsMessage.ioerror_save.format(str(e)))


class AsyncSpeech:
    """OpenAI-style async text-to-speech resource: ``client.audio.speech``."""

    def __init__(self, client):
        self.client = client

    async def create(
        self,
        *,
        input: str,
        voice: int | None = None,
        description: str | None = None,
        model: Versions | int | str = Versions.v1,
        chunk_size: float = 1.0,
        stream: bool = False,
        output_file: str | None = None,
    ) -> bytes | str | AsyncGenerator:
        version = Versions.from_value(model)
        request = _build_request(
            self.client, version, input, voice, description, chunk_size
        )

        if stream:
            if version == Versions.v1:
                raise ValueError(ErrorsMessage.tts_streaming_compatibility)
            return self._stream(request, output_file, version)

        content = await self.client._make_request(
            method=DjeliaRequest.tts.method,
            endpoint=DjeliaRequest.tts.endpoint.format(version.value),
            json=request.dict(),
        )
        if output_file:
            try:
                with open(output_file, "wb") as f:
                    f.write(content)
                return output_file
            except OSError as e:
                raise OSError(ErrorsMessage.ioerror_save.format(str(e)))
        return content

    async def _stream(
        self,
        request: TTSRequestV2,
        output_file: str | None,
        version: Versions,
    ) -> AsyncGenerator[bytes, None]:
        response = await self.client._make_streaming_request(
            method=DjeliaRequest.tts_stream.method,
            endpoint=DjeliaRequest.tts_stream.endpoint.format(version.value),
            json=request.dict(),
        )

        audio_chunks = []
        try:
            async for chunk in response.content.iter_chunked(8192):
                if chunk:
                    audio_chunks.append(chunk)
                    yield chunk
        finally:
            await response.close()

        if output_file:
            try:
                with open(output_file, "wb") as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
            except OSError as e:
                raise OSError(ErrorsMessage.ioerror_save.format(str(e)))


class TTS:
    """Deprecated. Use ``client.audio.speech`` instead."""

    def __init__(self, client):
        self.client = client

    def text_to_speech(
        self,
        request: TTSRequest | TTSRequestV2,
        output_file: str | None = None,
        stream: bool | None = False,
        version: Versions | None = Versions.v1,
    ) -> bytes | str | Generator:
        warnings.warn(
            "TTS.text_to_speech() is deprecated; "
            "use client.audio.speech.create(input=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        version = Versions.from_value(version)
        if version == Versions.v1:
            if not isinstance(request, TTSRequest):
                raise ValueError(ErrorsMessage.tts_v1_request_error)
            return self.client.audio.speech.create(
                input=request.text,
                voice=request.speaker,
                model=version,
                stream=bool(stream),
                output_file=output_file,
            )
        if not isinstance(request, TTSRequestV2):
            raise ValueError(ErrorsMessage.tts_v2_request_error)
        return self.client.audio.speech.create(
            input=request.text,
            description=request.description,
            chunk_size=request.chunk_size,
            model=version,
            stream=bool(stream),
            output_file=output_file,
        )


class AsyncTTS:
    """Deprecated. Use ``client.audio.speech`` instead."""

    def __init__(self, client):
        self.client = client

    async def text_to_speech(
        self,
        request: TTSRequest | TTSRequestV2,
        output_file: str | None = None,
        stream: bool | None = False,
        version: Versions | None = Versions.v1,
    ) -> bytes | str | AsyncGenerator:
        warnings.warn(
            "AsyncTTS.text_to_speech() is deprecated; "
            "use client.audio.speech.create(input=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        version = Versions.from_value(version)
        if version == Versions.v1:
            if not isinstance(request, TTSRequest):
                raise ValueError(ErrorsMessage.tts_v1_request_error)
            return await self.client.audio.speech.create(
                input=request.text,
                voice=request.speaker,
                model=version,
                stream=bool(stream),
                output_file=output_file,
            )
        if not isinstance(request, TTSRequestV2):
            raise ValueError(ErrorsMessage.tts_v2_request_error)
        return await self.client.audio.speech.create(
            input=request.text,
            description=request.description,
            chunk_size=request.chunk_size,
            model=version,
            stream=bool(stream),
            output_file=output_file,
        )
