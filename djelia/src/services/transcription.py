import json
import os
import warnings
from collections.abc import AsyncGenerator, Generator
from typing import BinaryIO

import aiohttp

from djelia.models import (DjeliaRequest, ErrorsMessage,
                           FrenchTranscriptionResponse, Params,
                           TranscriptionSegment, Versions)


class Transcriptions:
    """OpenAI-style transcription resource: ``client.audio.transcriptions``."""

    def __init__(self, client):
        self.client = client

    def create(
        self,
        *,
        file: str | BinaryIO,
        model: Versions | int | str = Versions.v2,
        translate_to_french: bool = False,
        stream: bool = False,
    ) -> list[TranscriptionSegment] | FrenchTranscriptionResponse | Generator:
        version = Versions.from_value(model)
        if stream:
            return self._stream(file, translate_to_french, version)

        try:
            params = {Params.translate_to_french: str(translate_to_french).lower()}
            if isinstance(file, str):
                with open(file, "rb") as f:
                    files = {Params.file: f}
                    response = self.client._make_request(
                        method=DjeliaRequest.transcribe.method,
                        endpoint=DjeliaRequest.transcribe.endpoint.format(
                            version.value
                        ),
                        files=files,
                        params=params,
                    )
            else:
                files = {Params.file: file}
                response = self.client._make_request(
                    method=DjeliaRequest.transcribe.method,
                    endpoint=DjeliaRequest.transcribe.endpoint.format(version.value),
                    files=files,
                    params=params,
                )
        except OSError as e:
            raise OSError(ErrorsMessage.ioerror_read.format(str(e)))

        data = response.json()
        return (
            FrenchTranscriptionResponse(**data)
            if translate_to_french
            else [TranscriptionSegment(**segment) for segment in data]
        )

    def _stream(
        self,
        file: str | BinaryIO,
        translate_to_french: bool,
        version: Versions,
    ) -> Generator[TranscriptionSegment | FrenchTranscriptionResponse, None, None]:
        try:
            params = {Params.translate_to_french: str(translate_to_french).lower()}
            if isinstance(file, str):
                with open(file, "rb") as f:
                    files = {Params.file: f}
                    response = self.client._make_request(
                        method=DjeliaRequest.transcribe_stream.method,
                        endpoint=DjeliaRequest.transcribe_stream.endpoint.format(
                            version.value
                        ),
                        files=files,
                        params=params,
                    )
            else:
                files = {Params.file: file}
                response = self.client._make_request(
                    method=DjeliaRequest.transcribe_stream.method,
                    endpoint=DjeliaRequest.transcribe_stream.endpoint.format(
                        version.value
                    ),
                    files=files,
                    params=params,
                )
        except OSError as e:
            raise OSError(ErrorsMessage.ioerror_read.format(str(e)))

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if isinstance(data, list):
                        for segment in data:
                            yield (
                                FrenchTranscriptionResponse(**segment)
                                if translate_to_french
                                else TranscriptionSegment(**segment)
                            )
                    else:
                        yield (
                            FrenchTranscriptionResponse(**data)
                            if translate_to_french
                            else TranscriptionSegment(**data)
                        )
                except json.JSONDecodeError:
                    continue


class AsyncTranscriptions:
    """OpenAI-style async transcription resource: ``client.audio.transcriptions``."""

    def __init__(self, client):
        self.client = client

    async def create(
        self,
        *,
        file: str | BinaryIO,
        model: Versions | int | str = Versions.v2,
        translate_to_french: bool = False,
        stream: bool = False,
    ) -> list[TranscriptionSegment] | FrenchTranscriptionResponse | AsyncGenerator:
        version = Versions.from_value(model)
        if stream:
            return self._stream(file, translate_to_french, version)

        try:
            data = aiohttp.FormData()
            if isinstance(file, str):
                with open(file, "rb") as f:
                    data.add_field(
                        Params.file, f.read(), filename=os.path.basename(file)
                    )
            else:
                data.add_field(Params.file, file.read(), filename=Params.filename)

            params = {Params.translate_to_french: str(translate_to_french).lower()}
            response_data = await self.client._make_request(
                method=DjeliaRequest.transcribe.method,
                endpoint=DjeliaRequest.transcribe.endpoint.format(version.value),
                data=data,
                params=params,
            )
        except OSError as e:
            raise OSError(ErrorsMessage.ioerror_read.format(str(e)))

        return (
            FrenchTranscriptionResponse(**response_data)
            if translate_to_french
            else [TranscriptionSegment(**segment) for segment in response_data]
        )

    async def _stream(
        self,
        file: str | BinaryIO,
        translate_to_french: bool,
        version: Versions,
    ) -> AsyncGenerator[TranscriptionSegment | FrenchTranscriptionResponse, None]:
        try:
            data = aiohttp.FormData()
            if isinstance(file, str):
                with open(file, "rb") as f:
                    data.add_field(
                        Params.file, f.read(), filename=os.path.basename(file)
                    )
            else:
                data.add_field(Params.file, file.read(), filename=Params.filename)

            params = {Params.translate_to_french: str(translate_to_french).lower()}
            response = await self.client._make_streaming_request(
                method=DjeliaRequest.transcribe_stream.method,
                endpoint=DjeliaRequest.transcribe_stream.endpoint.format(version.value),
                data=data,
                params=params,
            )
        except OSError as e:
            raise OSError(ErrorsMessage.ioerror_read.format(str(e)))

        try:
            if hasattr(response, "content") and response.content:
                async for line in response.content:
                    if line:
                        try:
                            line_str = line.decode("utf-8").strip()
                            if line_str:
                                segment_data = json.loads(line_str)
                                if isinstance(segment_data, list):
                                    for segment in segment_data:
                                        yield (
                                            FrenchTranscriptionResponse(**segment)
                                            if translate_to_french
                                            else TranscriptionSegment(**segment)
                                        )
                                else:
                                    yield (
                                        FrenchTranscriptionResponse(**segment_data)
                                        if translate_to_french
                                        else TranscriptionSegment(**segment_data)
                                    )
                        except Exception:  # I will comeback here for better handling
                            continue
            else:
                try:
                    response_text = await response.text()
                    if response_text.strip():
                        segment_data = json.loads(response_text)
                        if isinstance(segment_data, list):
                            for segment in segment_data:
                                yield (
                                    FrenchTranscriptionResponse(**segment)
                                    if translate_to_french
                                    else TranscriptionSegment(**segment)
                                )
                        else:
                            yield (
                                FrenchTranscriptionResponse(**segment_data)
                                if translate_to_french
                                else TranscriptionSegment(**segment_data)
                            )
                except Exception:
                    pass
        except Exception as e:
            raise e
        finally:
            try:
                if hasattr(response, "close"):
                    await response.close()
            except Exception:
                # there is a know issue here due to the server response
                pass


class Transcription:
    """Deprecated. Use ``client.audio.transcriptions`` instead."""

    def __init__(self, client):
        self.client = client

    def transcribe(
        self,
        audio_file: str | BinaryIO,
        translate_to_french: bool | None = False,
        stream: bool | None = False,
        version: Versions | None = Versions.v2,
    ) -> list[TranscriptionSegment] | FrenchTranscriptionResponse | Generator:
        warnings.warn(
            "Transcription.transcribe() is deprecated; "
            "use client.audio.transcriptions.create(file=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.client.audio.transcriptions.create(
            file=audio_file,
            model=version,
            translate_to_french=bool(translate_to_french),
            stream=bool(stream),
        )


class AsyncTranscription:
    """Deprecated. Use ``client.audio.transcriptions`` instead."""

    def __init__(self, client):
        self.client = client

    async def transcribe(
        self,
        audio_file: str | BinaryIO,
        translate_to_french: bool | None = False,
        stream: bool | None = False,
        version: Versions | None = Versions.v2,
    ) -> list[TranscriptionSegment] | FrenchTranscriptionResponse | AsyncGenerator:
        warnings.warn(
            "AsyncTranscription.transcribe() is deprecated; "
            "use client.audio.transcriptions.create(file=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.client.audio.transcriptions.create(
            file=audio_file,
            model=version,
            translate_to_french=bool(translate_to_french),
            stream=bool(stream),
        )
