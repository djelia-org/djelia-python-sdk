from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from djelia import Djelia, DjeliaAsync
from djelia.models import Language, Versions

from .config import Config
from .utils import Reporter

# ================================================
#                  Test registry
# ================================================

GROUP_ORDER: List[str] = [
    "translation",
    "transcription",
    "stream-transcription",
    "tts",
    "stream-tts",
    "version",
    "parallel",
]

GROUPS: Dict[str, Dict[str, Optional[str]]] = {
    "translation": {
        "label": "Translation",
        "sync": "translation_sync",
        "async": "translation_async",
    },
    "transcription": {
        "label": "Transcription",
        "sync": "transcription_sync",
        "async": "transcription_async",
    },
    "stream-transcription": {
        "label": "Streaming transcription",
        "sync": "streaming_transcription_sync",
        "async": "streaming_transcription_async",
    },
    "tts": {
        "label": "Text-to-speech",
        "sync": "tts_sync",
        "async": "tts_async",
    },
    "stream-tts": {
        "label": "Streaming TTS",
        "sync": "streaming_tts_sync",
        "async": "streaming_tts_async",
    },
    "version": {
        "label": "Version management",
        "sync": "version_management",
        "async": None,
    },
    "parallel": {
        "label": "Parallel operations",
        "sync": None,
        "async": "parallel_operations",
    },
}


def _short(text: str, limit: int = 32) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _transcription_detail(transcription) -> str:
    if isinstance(transcription, list):
        if transcription:
            return f"{len(transcription)} segments · '{_short(transcription[0].text)}'"
        return "0 segments"
    if hasattr(transcription, "text"):
        return f"'{_short(transcription.text)}'"
    return "unexpected format"


def _filesize(path: str) -> str:
    try:
        return f"{os.path.getsize(path):,} bytes"
    except OSError:
        return "written"


class DjeliaTestSuite:
    """Exercises the OpenAI-style Djelia SDK surface and reports live metrics."""

    def __init__(self, config: Config, reporter: Reporter):
        self.config = config
        self.reporter = reporter
        self.sync_client = Djelia(api_key=config.api_key)
        self.async_client = DjeliaAsync(api_key=config.api_key)

        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._generated: List[Path] = []

        self.samples = [
            ("Hello, how are you?", Language.ENGLISH, Language.BAMBARA),
            ("Bonjour, comment allez-vous?", Language.FRENCH, Language.BAMBARA),
            ("Good morning", Language.ENGLISH, Language.FRENCH),
        ]
        self.tts_text = config.tts_text
        self.speakers = config.speakers

    # ---------
    # Helpers #
    # --------
    def _out(self, name: str) -> str:
        path = self.output_dir / name
        self._generated.append(path)
        return str(path)

    def cleanup(self) -> None:
        if self.config.keep_audio:
            if self._generated:
                self.reporter.info(
                    f"kept {len(self._generated)} audio file(s) in {self.output_dir}/"
                )
            return
        removed = 0
        for path in self._generated:
            try:
                path.unlink()
                removed += 1
            except OSError:
                pass
        try:
            self.output_dir.rmdir()
        except OSError:
            pass
        if removed:
            self.reporter.info(f"cleaned up {removed} generated audio file(s)")

    def validate(self) -> bool:
        ok = True
        if not self.config.api_key:
            self.reporter.fail("DJELIA_API_KEY is not set")
            ok = False
        if not os.path.exists(self.config.audio_file_path):
            self.reporter.fail(f"audio file not found: {self.config.audio_file_path}")
            ok = False
        if ok:
            self.reporter.ok("API key and audio file present")
        return ok

    # --------------
    # Translation #
    # -------------
    def translation_sync(self) -> None:
        with self.reporter.case("Translation · sync", "translation") as case:
            with case.op("languages", "supported-languages") as op:
                languages = self.sync_client.translations.list_languages()
                op.set(f"{len(languages)} languages")
            for text, source, target in self.samples:
                with case.op("translate", f"{source.value}→{target.value}") as op:
                    response = self.sync_client.translations.create(
                        text=text, source=source, target=target, model=Versions.v1
                    )
                    op.set(f"'{_short(text)}' → '{_short(response.text)}'")
            case.done(f"{len(self.samples)} translations · {len(languages)} languages")

    async def translation_async(self) -> None:
        with self.reporter.case("Translation · async", "translation") as case:
            async with self.async_client as client:
                with case.op("languages", "supported-languages") as op:
                    languages = await client.translations.list_languages()
                    op.set(f"{len(languages)} languages")
                for text, source, target in self.samples:
                    with case.op("translate", f"{source.value}→{target.value}") as op:
                        response = await client.translations.create(
                            text=text, source=source, target=target, model=Versions.v1
                        )
                        op.set(f"'{_short(text)}' → '{_short(response.text)}'")
            case.done(f"{len(self.samples)} translations · {len(languages)} languages")

    # --------------
    # Transcription #
    # --------------
    def transcription_sync(self) -> None:
        with self.reporter.case("Transcription · sync", "transcription") as case:
            for version in (Versions.v1, Versions.v2):
                with case.op("transcribe", f"v{version.value}") as op:
                    transcription = self.sync_client.audio.transcriptions.create(
                        file=self.config.audio_file_path, model=version
                    )
                    op.set(_transcription_detail(transcription))
                if version == Versions.v2:
                    with case.op("transcribe", "v2 → french") as op:
                        fr = self.sync_client.audio.transcriptions.create(
                            file=self.config.audio_file_path,
                            translate_to_french=True,
                            model=version,
                        )
                        op.set(f"'{_short(fr.text)}'")
            case.done("v1 + v2 (with french)")

    async def transcription_async(self) -> None:
        with self.reporter.case("Transcription · async", "transcription") as case:
            async with self.async_client as client:
                for version in (Versions.v1, Versions.v2):
                    with case.op("transcribe", f"v{version.value}") as op:
                        transcription = await client.audio.transcriptions.create(
                            file=self.config.audio_file_path, model=version
                        )
                        op.set(_transcription_detail(transcription))
                    if version == Versions.v2:
                        with case.op("transcribe", "v2 → french") as op:
                            fr = await client.audio.transcriptions.create(
                                file=self.config.audio_file_path,
                                translate_to_french=True,
                                model=version,
                            )
                            op.set(f"'{_short(fr.text)}'")
            case.done("v1 + v2 (with french)")

    # -----------------------
    # Streaming transcription #
    # -----------------------
    def streaming_transcription_sync(self) -> None:
        with self.reporter.case(
            "Streaming transcription · sync", "stream-transcription"
        ) as case:
            limit = self.config.max_stream_segments
            for version in (Versions.v1, Versions.v2):
                with case.op("stream", f"transcribe v{version.value}") as op:
                    count = 0
                    for segment in self.sync_client.audio.transcriptions.create(
                        file=self.config.audio_file_path, stream=True, model=version
                    ):
                        count += 1
                        case.note(
                            f"seg {count} {segment.start:.2f}-{segment.end:.2f}s: "
                            f"{_short(segment.text)}"
                        )
                        if count >= limit:
                            break
                    op.set(f"{count} segments (first {limit})")
            case.done("v1 + v2 streamed")

    async def streaming_transcription_async(self) -> None:
        with self.reporter.case(
            "Streaming transcription · async", "stream-transcription"
        ) as case:
            limit = self.config.max_stream_segments
            async with self.async_client as client:
                for version in (Versions.v1, Versions.v2):
                    with case.op("stream", f"transcribe v{version.value}") as op:
                        count = 0
                        generator = await client.audio.transcriptions.create(
                            file=self.config.audio_file_path, stream=True, model=version
                        )
                        async for segment in generator:
                            count += 1
                            case.note(
                                f"seg {count} {segment.start:.2f}-{segment.end:.2f}s: "
                                f"{_short(segment.text)}"
                            )
                            if count >= limit:
                                break
                        op.set(f"{count} segments (first {limit})")
            case.done("v1 + v2 streamed")

    # ---------------
    # Text-to-speech #
    # ---------------
    def tts_sync(self) -> None:
        with self.reporter.case("Text-to-speech · sync", "tts") as case:
            with case.op("tts", "v1") as op:
                path = self.sync_client.audio.speech.create(
                    input=self.tts_text,
                    voice=1,
                    output_file=self._out(f"tts_sync_v1_{uuid4().hex}.wav"),
                    model=Versions.v1,
                )
                op.set(_filesize(path))
            for speaker in self.speakers:
                with case.op("tts", f"v2 {speaker}") as op:
                    path = self.sync_client.audio.speech.create(
                        input=self.tts_text,
                        description=f"{speaker} speaks with natural tone",
                        output_file=self._out(
                            f"tts_sync_v2_{speaker}_{uuid4().hex}.wav"
                        ),
                        model=Versions.v2,
                    )
                    op.set(_filesize(path))
            case.done(f"v1 + {len(self.speakers)} v2 speakers")

    async def tts_async(self) -> None:
        with self.reporter.case("Text-to-speech · async", "tts") as case:
            async with self.async_client as client:
                with case.op("tts", "v1") as op:
                    path = await client.audio.speech.create(
                        input=self.tts_text,
                        voice=1,
                        output_file=self._out(f"tts_async_v1_{uuid4().hex}.wav"),
                        model=Versions.v1,
                    )
                    op.set(_filesize(path))
                for speaker in self.speakers:
                    with case.op("tts", f"v2 {speaker}") as op:
                        path = await client.audio.speech.create(
                            input=self.tts_text,
                            description=f"{speaker} speaks with natural tone",
                            output_file=self._out(
                                f"tts_async_v2_{speaker}_{uuid4().hex}.wav"
                            ),
                            model=Versions.v2,
                        )
                        op.set(_filesize(path))
            case.done(f"v1 + {len(self.speakers)} v2 speakers")

    # --------------------------
    # Streaming text-to-speech #
    # --------------------------
    def streaming_tts_sync(self) -> None:
        with self.reporter.case("Streaming TTS · sync", "stream-tts") as case:
            limit = self.config.max_stream_chunks
            with case.op("stream", "tts v2") as op:
                chunks = 0
                total = 0
                for chunk in self.sync_client.audio.speech.create(
                    input=self.tts_text,
                    description=f"{self.speakers[0]} speaks with natural conversational tone",
                    output_file=self._out(f"stream_tts_sync_{uuid4().hex}.wav"),
                    stream=True,
                    model=Versions.v2,
                ):
                    chunks += 1
                    total += len(chunk)
                    case.note(f"chunk {chunks}: {len(chunk):,} bytes")
                    if chunks >= limit:
                        break
                op.set(f"{chunks} chunks · {total:,} bytes")
            case.done(f"{chunks} chunks streamed")

    async def streaming_tts_async(self) -> None:
        with self.reporter.case("Streaming TTS · async", "stream-tts") as case:
            limit = self.config.max_stream_chunks
            async with self.async_client as client:
                with case.op("stream", "tts v2") as op:
                    chunks = 0
                    total = 0
                    generator = await client.audio.speech.create(
                        input=self.tts_text,
                        description=f"{self.speakers[0]} speaks with clear natural tone",
                        output_file=self._out(f"stream_tts_async_{uuid4().hex}.wav"),
                        stream=True,
                        model=Versions.v2,
                    )
                    async for chunk in generator:
                        chunks += 1
                        total += len(chunk)
                        case.note(f"chunk {chunks}: {len(chunk):,} bytes")
                        if chunks >= limit:
                            break
                    op.set(f"{chunks} chunks · {total:,} bytes")
            case.done(f"{chunks} chunks streamed")

    # --------------------
    # Version management #
    # -------------------
    def version_management(self) -> None:
        with self.reporter.case("Version management · sync", "version") as case:
            self.reporter.info(f"latest version: {Versions.latest()}")
            self.reporter.info(
                f"available: {[str(v) for v in Versions.all_versions()]}"
            )
            with case.op("translate", "v1") as op:
                result = self.sync_client.translations.create(
                    text="Hello world",
                    source=Language.ENGLISH,
                    target=Language.BAMBARA,
                    model=Versions.v1,
                )
                op.set(f"'{_short(result.text)}'")
            for version in (Versions.v1, Versions.v2):
                with case.op("transcribe", f"v{version.value}") as op:
                    transcription = self.sync_client.audio.transcriptions.create(
                        file=self.config.audio_file_path, model=version
                    )
                    op.set(_transcription_detail(transcription))
            with case.op("tts", "v1") as op:
                path = self.sync_client.audio.speech.create(
                    input=self.tts_text,
                    voice=1,
                    output_file=self._out(f"tts_v1_{uuid4().hex}.wav"),
                    model=Versions.v1,
                )
                op.set(_filesize(path))
            with case.op("tts", "v2") as op:
                path = self.sync_client.audio.speech.create(
                    input=self.tts_text,
                    description=f"{self.speakers[0]} speaks with natural tone",
                    output_file=self._out(f"tts_v2_{uuid4().hex}.wav"),
                    model=Versions.v2,
                )
                op.set(_filesize(path))
            case.done("v1/v2 across translate, transcribe, tts")

    # ---------------------
    # Parallel operations #
    # ---------------------
    async def parallel_operations(self) -> None:
        with self.reporter.case("Parallel operations · async", "parallel") as case:
            async with self.async_client as client:
                with case.op("gather", "4 concurrent ops") as op:
                    results = await asyncio.gather(
                        client.translations.list_languages(),
                        client.translations.create(
                            text="Hello",
                            source=Language.ENGLISH,
                            target=Language.BAMBARA,
                            model=Versions.v1,
                        ),
                        client.audio.transcriptions.create(
                            file=self.config.audio_file_path, model=Versions.v1
                        ),
                        client.audio.speech.create(
                            input=self.tts_text,
                            description=f"{self.speakers[0]} speaks with clear speaking tone",
                            output_file=self._out(f"parallel_tts_{uuid4().hex}.wav"),
                            model=Versions.v2,
                        ),
                        return_exceptions=True,
                    )
                    succeeded = sum(1 for r in results if not isinstance(r, Exception))
                    op.set(f"{succeeded}/{len(results)} succeeded")

            names = ["languages", "translation", "transcription", "tts"]
            failed = []
            for name, result in zip(names, results):
                if isinstance(result, Exception):
                    case.note(f"[red]{name}: {result}[/]")
                    failed.append(name)
                else:
                    case.note(f"{name}: {type(result).__name__}")
            if failed:
                raise RuntimeError(f"failed: {', '.join(failed)}")
            case.done("4 concurrent operations")

    # ---------------
    # Orchestration #
    # ---------------
    def run(self, groups: List[str], mode: str) -> None:
        selected = [g for g in GROUP_ORDER if g in groups]

        for key in selected:
            method = GROUPS[key]["sync"]
            if mode in ("sync", "both") and method:
                getattr(self, method)()

        async_methods = [
            GROUPS[key]["async"]
            for key in selected
            if mode in ("async", "both") and GROUPS[key]["async"]
        ]
        if async_methods:
            asyncio.run(self._run_async(async_methods))

        self.cleanup()

    async def _run_async(self, method_names: List[str]) -> None:
        for name in method_names:
            await getattr(self, name)()
