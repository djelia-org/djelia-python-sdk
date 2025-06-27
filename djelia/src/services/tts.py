from collections.abc import AsyncGenerator, Generator

# from djelia.config.settings import VALID_SPEAKER_IDS, VALID_TTS_V2_SPEAKERS
from djelia.models import (DjeliaRequest, ErrorsMessage, TTSRequest,
                           TTSRequestV2, Versions)
from djelia.utils.exceptions import SpeakerError


class TTS:
    def __init__(self, client):
        self.client = client

    def text_to_speech(
        self,
        request: TTSRequest | TTSRequestV2,
        output_file: str | None = None,
        stream: bool | None = False,
        version: Versions | None = Versions.v1,
    ) -> bytes | str | Generator:
        if version == Versions.v1:
            if not isinstance(request, TTSRequest):
                raise ValueError(ErrorsMessage.tts_v1_request_error)
            if request.speaker not in self.client.settings.valid_speaker_ids:
                raise SpeakerError(
                    ErrorsMessage.speaker_id_error.format(
                        self.client.settings.valid_speaker_ids, request.speaker
                    )
                )
        else:
            if not isinstance(request, TTSRequestV2):
                raise ValueError(ErrorsMessage.tts_v2_request_error)
            speaker_found = any(
                speaker.lower() in request.description.lower()
                for speaker in self.client.settings.valid_tts_v2_speakers
            )
            if not speaker_found:
                raise SpeakerError(
                    ErrorsMessage.speaker_description_error.format(
                        self.client.settings.valid_tts_v2_speakers
                    )
                )

        if not stream:
            data = request.dict()
            response = self.client._make_request(
                method=DjeliaRequest.tts.method,
                endpoint=DjeliaRequest.tts.endpoint.format(version.value),
                json=data,
            )

            if output_file:
                try:
                    with open(output_file, "wb") as f:
                        f.write(response.content)
                    return output_file
                except OSError as e:
                    raise OSError(ErrorsMessage.ioerror_save.format(str(e)))
            else:
                return response.content
        else:
            if version == Versions.v1:
                raise ValueError(ErrorsMessage.tts_streaming_conpatibility)
            return self._stream_text_to_speech(request, output_file, version)

    def _stream_text_to_speech(
        self,
        request: TTSRequestV2,
        output_file: str | None = None,
        version: Versions | None = Versions.v2,
    ) -> Generator[bytes, None, None]:
        data = request.dict()
        response = self.client._make_request(
            method=DjeliaRequest.tts_stream.method,
            endpoint=DjeliaRequest.tts_stream.endpoint.format(version.value),
            json=data,
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


class AsyncTTS:
    def __init__(self, client):
        self.client = client

    async def text_to_speech(
        self,
        request: TTSRequest | TTSRequestV2,
        output_file: str | None = None,
        stream: bool | None = False,
        version: Versions | None = Versions.v1,
    ) -> bytes | str | AsyncGenerator:
        if version == Versions.v1:
            if not isinstance(request, TTSRequest):
                raise ValueError(ErrorsMessage.tts_v1_request_error)
            if request.speaker not in self.client.settings.valid_speaker_ids:
                raise SpeakerError(
                    ErrorsMessage.speaker_id_error.format(
                        self.client.settings.valid_speaker_ids, request.speaker
                    )
                )
        else:
            if not isinstance(request, TTSRequestV2):
                raise ValueError(ErrorsMessage.tts_v2_request_error)
            speaker_found = any(
                speaker.lower() in request.description.lower()
                for speaker in self.client.settings.valid_tts_v2_speakers
            )
            if not speaker_found:
                raise SpeakerError(
                    ErrorsMessage.speaker_description_error.format(
                        self.client.settings.valid_tts_v2_speakers
                    )
                )

        if not stream:
            request_data = request.dict()
            content = await self.client._make_request(
                method=DjeliaRequest.tts.method,
                endpoint=DjeliaRequest.tts.endpoint.format(version.value),
                json=request_data,
            )

            if output_file:
                try:
                    with open(output_file, "wb") as f:
                        f.write(content)
                    return output_file
                except OSError as e:
                    raise OSError(ErrorsMessage.ioerror_save.format(str(e)))
            else:
                return content
        else:
            if version == Versions.v1:
                raise ValueError(ErrorsMessage.tts_streaming_conpatibility)
            # FIXED: Remove 'await' here - async generators should not be awaited when returned
            return self._stream_text_to_speech(request, output_file, version)

    async def _stream_text_to_speech(
        self,
        request: TTSRequestV2,
        output_file: str | None = None,
        version: Versions | None = Versions.v2,
    ) -> AsyncGenerator[bytes, None]:
        request_data = request.dict()
        response = await self.client._make_streaming_request(
            method=DjeliaRequest.tts_stream.method,
            endpoint=DjeliaRequest.tts_stream.endpoint.format(version.value),
            json=request_data,
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
