import asyncio
import logging
import os
import traceback
from uuid import uuid4

from djelia import Djelia, DjeliaAsync
from djelia.models import (Language, SupportedLanguageSchema,
                           TranslationRequest, TranslationResponse, TTSRequest,
                           TTSRequestV2, Versions)

from .config import Config
from .utils import (ConsoleColor, handle_transcription_result, print_error,
                    print_info, print_success, print_summary, process_result)

# ================================================
#                  Djelia Cookbook
# ================================================


class DjeliaCookbook:
    def __init__(self, config: Config):
        self.config = config
        self.sync_client = Djelia(api_key=config.api_key)
        self.async_client = DjeliaAsync(api_key=config.api_key)
        self.test_results = {}

        self.translation_samples = [
            ("Hello, how are you?", Language.ENGLISH, Language.BAMBARA),
            ("Bonjour, comment allez-vous?", Language.FRENCH, Language.BAMBARA),
            ("Good morning", Language.ENGLISH, Language.FRENCH),
        ]
        self.bambara_tts_text = "Aw ni ce, i ka kɛnɛ wa?"
        self.supported_speakers = ["Moussa", "Sekou", "Seydou"]

    # ------------------------------
    # Setup Validation
    # ------------------------------

    def validate_setup(self) -> bool:
        valid = True

        if not self.config.api_key:
            print_error("DJELIA_API_KEY not found")
            valid = False

        if not os.path.exists(self.config.audio_file_path):
            print_error(f"Audio file not found: {self.config.audio_file_path}")
            valid = False

        if valid:
            print_success("API Key and audio file loaded")

        return valid

    # ------------------------------
    # Translation Tests
    # ------------------------------

    def test_translation_sync(self) -> None:
        test_name = "Sync Translation"
        print(
            f"{ConsoleColor.CYAN}\n{'SYNCHRONOUS TRANSLATION':^60}{ConsoleColor.RESET}"
        )

        try:
            languages: list[SupportedLanguageSchema] = (
                self.sync_client.translation.get_supported_languages()
            )
            print_success(f"Supported languages: {len(languages)}")

            for text, source, target in self.translation_samples:
                request = TranslationRequest(text=text, source=source, target=target)
                response: TranslationResponse = self.sync_client.translation.translate(
                    request=request, version=Versions.v1
                )
                print_success(
                    f"{source.value} → {target.value}: "
                    f"'{text}' → '{ConsoleColor.YELLOW}{response.text}{ConsoleColor.RESET}'"
                )

            self.test_results[test_name] = (
                "Success",
                f"{len(self.translation_samples)} translations",
            )

        except Exception as e:
            print_error(f"Translation error: {e}")
            self.test_results[test_name] = ("Failed", str(e))
            logging.error(f"Traceback:\n{traceback.format_exc()}")

    async def test_translation_async(self) -> None:
        test_name = "Async Translation"
        print(
            f"{ConsoleColor.PURPLE}\n{'ASYNCHRONOUS TRANSLATION':^60}{ConsoleColor.RESET}"
        )

        async with self.async_client as client:
            try:
                languages = await client.translation.get_supported_languages()
                print_success(f"Supported languages (async): {len(languages)}")

                for text, source, target in self.translation_samples:
                    request = TranslationRequest(
                        text=text, source=source, target=target
                    )
                    response = await client.translation.translate(
                        request=request, version=Versions.v1
                    )
                    print_success(
                        f"{source.value} → {target.value} (async): "
                        f"'{text}' → '{ConsoleColor.YELLOW}{response.text}{ConsoleColor.RESET}'"
                    )

                self.test_results[test_name] = (
                    "Success",
                    f"{len(self.translation_samples)} translations",
                )

            except Exception as e:
                print_error(f"Async translation error: {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # Transcription Tests
    # ------------------------------

    def test_transcription_sync(self) -> None:
        test_name = "Sync Transcription"
        print(
            f"{ConsoleColor.CYAN}\n{'SYNCHRONOUS TRANSCRIPTION':^60}{ConsoleColor.RESET}"
        )

        if not os.path.exists(self.config.audio_file_path):
            print_error("Audio file missing")
            self.test_results[test_name] = ("Failed", "Missing audio file")
            return

        for version in [Versions.v1, Versions.v2]:
            try:
                print_info(f"Testing non-streaming v{version.value}")
                transcription = self.sync_client.transcription.transcribe(
                    self.config.audio_file_path, version=version
                )
                handle_transcription_result(transcription, f"v{version.value}")

                if version == Versions.v2:
                    print_info("Testing French translation")
                    transcription_fr = self.sync_client.transcription.transcribe(
                        self.config.audio_file_path,
                        translate_to_french=True,
                        version=version,
                    )
                    print_success(
                        f"French translation (v{version.value}): "
                        f"'{ConsoleColor.YELLOW}{transcription_fr.text}{ConsoleColor.RESET}'"
                    )

                self.test_results[test_name] = (
                    "Success",
                    f"v{version.value} completed",
                )

            except Exception as e:
                print_error(f"Transcription error (v{version.value}): {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    async def test_transcription_async(self) -> None:
        test_name = "Async Transcription"
        print(
            f"{ConsoleColor.PURPLE}\n{'ASYNCHRONOUS TRANSCRIPTION':^60}{ConsoleColor.RESET}"
        )

        if not os.path.exists(self.config.audio_file_path):
            print_error("Audio file missing")
            self.test_results[test_name] = ("Failed", "Missing audio file")
            return

        async with self.async_client as client:
            for version in [Versions.v1, Versions.v2]:
                try:
                    print_info(f"Testing non-streaming v{version.value}")
                    transcription = await client.transcription.transcribe(
                        self.config.audio_file_path, version=version
                    )
                    handle_transcription_result(
                        transcription, f"v{version.value} (async)"
                    )

                    if version == Versions.v2:
                        print_info("Testing French translation")
                        transcription_fr = await client.transcription.transcribe(
                            self.config.audio_file_path,
                            translate_to_french=True,
                            version=version,
                        )
                        print_success(
                            f"French translation (async): "
                            f"'{ConsoleColor.YELLOW}{transcription_fr.text}{ConsoleColor.RESET}'"
                        )

                    self.test_results[test_name] = (
                        "Success",
                        f"v{version.value} completed",
                    )

                except Exception as e:
                    print_error(f"Async transcription error (v{version.value}): {e}")
                    self.test_results[test_name] = ("Failed", str(e))
                    logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # Streaming Transcription
    # ------------------------------

    def test_streaming_transcription_sync(self) -> None:
        test_name = "Sync Streaming Transcription"
        print(
            f"{ConsoleColor.CYAN}\n{'SYNCHRONOUS STREAMING TRANSCRIPTION':^60}{ConsoleColor.RESET}"
        )

        if not os.path.exists(self.config.audio_file_path):
            print_error("Audio file missing")
            self.test_results[test_name] = ("Failed", "Missing audio file")
            return

        for version in [Versions.v1, Versions.v2]:
            try:
                print_info(f"Testing streaming v{version.value}")
                segment_count = 0

                for segment in self.sync_client.transcription.transcribe(
                    self.config.audio_file_path, stream=True, version=version
                ):
                    segment_count += 1
                    print_success(
                        f"Segment {segment_count}: "
                        f"{segment.start:.2f}s-{segment.end:.2f}s: "
                        f"'{ConsoleColor.YELLOW}{segment.text}{ConsoleColor.RESET}'"
                    )

                    if segment_count >= self.config.max_stream_segments:
                        print_info(
                            f"Showing first {self.config.max_stream_segments} segments"
                        )
                        break

                print_success(f"Streaming complete: {segment_count} segments")

                if version == Versions.v2:
                    print_info("Testing streaming French translation")
                    segment_count = 0

                    for segment in self.sync_client.transcription.transcribe(
                        self.config.audio_file_path,
                        stream=True,
                        translate_to_french=True,
                        version=version,
                    ):
                        segment_count += 1
                        text = segment.text
                        print_success(
                            f"French Segment {segment_count}: "
                            f"'{ConsoleColor.YELLOW}{text}{ConsoleColor.RESET}'"
                        )

                        if segment_count >= self.config.max_stream_segments:
                            print_info(
                                f"Showing first {self.config.max_stream_segments} segments"
                            )
                            break

                    print_success(
                        f"French streaming complete: {segment_count} segments"
                    )

                self.test_results[test_name] = (
                    "Success",
                    f"v{version.value} completed",
                )

            except Exception as e:
                print_error(f"Streaming error (v{version.value}): {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    async def test_streaming_transcription_async(self) -> None:
        test_name = "Async Streaming Transcription"
        print(
            f"{ConsoleColor.PURPLE}\n{'ASYNCHRONOUS STREAMING TRANSCRIPTION':^60}{ConsoleColor.RESET}"
        )

        if not os.path.exists(self.config.audio_file_path):
            print_error("Audio file missing")
            self.test_results[test_name] = ("Failed", "Missing audio file")
            return

        async with self.async_client as client:
            for version in [Versions.v1, Versions.v2]:
                try:
                    print_info(f"Testing streaming v{version.value}")
                    segment_count = 0

                    generator = await client.transcription.transcribe(
                        self.config.audio_file_path, stream=True, version=version
                    )

                    async for segment in generator:
                        segment_count += 1
                        print_success(
                            f"Segment {segment_count}: "
                            f"{segment.start:.2f}s-{segment.end:.2f}s: "
                            f"'{ConsoleColor.YELLOW}{segment.text}{ConsoleColor.RESET}'"
                        )

                        if segment_count >= self.config.max_stream_segments:
                            print_info(
                                f"Showing first {self.config.max_stream_segments} segments"
                            )
                            break

                    print_success(f"Streaming complete: {segment_count} segments")

                    if version == Versions.v2:
                        print_info("Testing streaming French translation")
                        segment_count = 0

                        generator = await client.transcription.transcribe(
                            self.config.audio_file_path,
                            stream=True,
                            translate_to_french=True,
                            version=version,
                        )

                        async for segment in generator:
                            segment_count += 1
                            text = segment.text
                            print_success(
                                f"French Segment {segment_count}: "
                                f"'{ConsoleColor.YELLOW}{text}{ConsoleColor.RESET}'"
                            )

                            if segment_count >= self.config.max_stream_segments:
                                print_info(
                                    f"Showing first {self.config.max_stream_segments} segments"
                                )
                                break

                        print_success(
                            f"French streaming complete: {segment_count} segments"
                        )

                    self.test_results[test_name] = (
                        "Success",
                        f"v{version.value} completed",
                    )

                except Exception as e:
                    print_error(f"Async streaming error (v{version.value}): {e}")
                    self.test_results[test_name] = ("Failed", str(e))
                    logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # TTS Tests
    # ------------------------------

    def test_tts_sync(self) -> None:
        test_name = "Sync TTS"
        print(
            f"{ConsoleColor.CYAN}\n{'SYNCHRONOUS TEXT-TO-SPEECH':^60}{ConsoleColor.RESET}"
        )

        try:
            tts_request_v1 = TTSRequest(text=self.bambara_tts_text, speaker=1)
            audio_file_v1 = self.sync_client.tts.text_to_speech(
                request=tts_request_v1,
                output_file=f"tts_sync_v1_{uuid4().hex}.wav",
                version=Versions.v1,
            )
            print_success(
                f"TTS v1 saved: {ConsoleColor.BLUE}{audio_file_v1}{ConsoleColor.RESET}"
            )

            for speaker in self.supported_speakers:
                tts_request_v2 = TTSRequestV2(
                    text=self.bambara_tts_text,
                    description=f"{speaker} speaks with natural tone",
                    chunk_size=1.0,
                )
                audio_file_v2 = self.sync_client.tts.text_to_speech(
                    request=tts_request_v2,
                    output_file=f"tts_sync_v2_{speaker}_{uuid4().hex}.wav",
                    version=Versions.v2,
                )
                print_success(
                    f"TTS v2 ({speaker}): {ConsoleColor.BLUE}{audio_file_v2}{ConsoleColor.RESET}"
                )

            self.test_results[test_name] = (
                "Success",
                f"{len(self.supported_speakers)} speakers",
            )

        except Exception as e:
            print_error(f"TTS error: {e}")
            self.test_results[test_name] = ("Failed", str(e))
            logging.error(f"Traceback:\n{traceback.format_exc()}")

    async def test_tts_async(self) -> None:
        test_name = "Async TTS"
        print(
            f"{ConsoleColor.PURPLE}\n{'ASYNCHRONOUS TEXT-TO-SPEECH':^60}{ConsoleColor.RESET}"
        )

        async with self.async_client as client:
            try:
                tts_request_v1 = TTSRequest(text=self.bambara_tts_text, speaker=1)
                audio_file_v1 = await client.tts.text_to_speech(
                    request=tts_request_v1,
                    output_file=f"tts_async_v1_{uuid4().hex}.wav",
                    version=Versions.v1,
                )
                print_success(
                    f"TTS v1 saved: {ConsoleColor.BLUE}{audio_file_v1}{ConsoleColor.RESET}"
                )

                for speaker in self.supported_speakers:
                    tts_request_v2 = TTSRequestV2(
                        text=self.bambara_tts_text,
                        description=f"{speaker} speaks with natural tone",
                        chunk_size=0.5,
                    )
                    audio_file_v2 = await client.tts.text_to_speech(
                        request=tts_request_v2,
                        output_file=f"tts_async_v2_{speaker}_{uuid4().hex}.wav",
                        version=Versions.v2,
                    )
                    print_success(
                        f"TTS v2 ({speaker}): {ConsoleColor.BLUE}{audio_file_v2}{ConsoleColor.RESET}"
                    )

                self.test_results[test_name] = (
                    "Success",
                    f"{len(self.supported_speakers)} speakers",
                )

            except Exception as e:
                print_error(f"Async TTS error: {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # Streaming TTS
    # ------------------------------

    def test_streaming_tts_sync(self) -> None:
        test_name = "Sync Streaming TTS"
        print(
            f"{ConsoleColor.CYAN}\n{'SYNCHRONOUS STREAMING TTS':^60}{ConsoleColor.RESET}"
        )

        try:
            tts_request = TTSRequestV2(
                text=self.bambara_tts_text,
                description=f"{self.supported_speakers[0]} speaks with natural conversational tone",
            )
            chunk_count = 0
            total_bytes = 0

            for audio_chunk in self.sync_client.tts.text_to_speech(
                request=tts_request,
                output_file=f"stream_tts_sync_{uuid4().hex}.wav",
                stream=True,
                version=Versions.v2,
            ):
                chunk_count += 1
                total_bytes += len(audio_chunk)
                print_success(f"Chunk {chunk_count}: {len(audio_chunk):,} bytes")

                if chunk_count >= self.config.max_stream_chunks:
                    print_info(f"Showing first {self.config.max_stream_chunks} chunks")
                    break

            print_success(
                f"Streaming complete: {chunk_count} chunks, "
                f"{ConsoleColor.BLUE}{total_bytes:,} bytes{ConsoleColor.RESET}"
            )
            self.test_results[test_name] = ("Success", f"{chunk_count} chunks")

        except Exception as e:
            print_error(f"Streaming TTS error: {e}")
            self.test_results[test_name] = ("Failed", str(e))
            logging.error(f"Traceback:\n{traceback.format_exc()}")

    async def test_streaming_tts_async(self) -> None:
        test_name = "Async Streaming TTS"
        print(
            f"{ConsoleColor.PURPLE}\n{'ASYNCHRONOUS STREAMING TTS':^60}{ConsoleColor.RESET}"
        )

        async with self.async_client as client:
            try:
                tts_request = TTSRequestV2(
                    text=self.bambara_tts_text,
                    description=f"{self.supported_speakers[0]} speaks with clear natural tone",
                )
                chunk_count = 0
                total_bytes = 0

                generator = await client.tts.text_to_speech(
                    request=tts_request,
                    output_file=f"stream_tts_async_{uuid4().hex}.wav",
                    stream=True,
                    version=Versions.v2,
                )

                async for audio_chunk in generator:
                    chunk_count += 1
                    total_bytes += len(audio_chunk)
                    print_success(f"Chunk {chunk_count}: {len(audio_chunk):,} bytes")

                    if chunk_count >= self.config.max_stream_chunks:
                        print_info(
                            f"Showing first {self.config.max_stream_chunks} chunks"
                        )
                        break

                print_success(
                    f"Streaming complete: {chunk_count} chunks, "
                    f"{ConsoleColor.BLUE}{total_bytes:,} bytes{ConsoleColor.RESET}"
                )
                self.test_results[test_name] = ("Success", f"{chunk_count} chunks")

            except Exception as e:
                print_error(f"Async streaming TTS error: {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # Advanced Features
    # ------------------------------

    async def test_parallel_operations(self) -> None:
        test_name = "Parallel Operations"
        print(
            f"{ConsoleColor.CYAN}\n{'PARALLEL API OPERATIONS':^60}{ConsoleColor.RESET}"
        )

        async with self.async_client as client:
            try:
                print_info("Executing parallel operations...")

                translation_request = TranslationRequest(
                    text="Hello", source=Language.ENGLISH, target=Language.BAMBARA
                )

                tts_request = TTSRequestV2(
                    text=self.bambara_tts_text,
                    description=f"{self.supported_speakers[0]} speaks with clear speaking tone",
                )

                results = await asyncio.gather(
                    client.translation.get_supported_languages(),
                    client.translation.translate(
                        translation_request, version=Versions.v1
                    ),
                    client.transcription.transcribe(
                        self.config.audio_file_path, version=Versions.v1
                    ),
                    client.tts.text_to_speech(
                        tts_request,
                        output_file=f"parallel_tts_{uuid4().hex}.wav",
                        version=Versions.v2,
                    ),
                    return_exceptions=True,
                )

                print(f"\n{ConsoleColor.CYAN}Parallel Results:{ConsoleColor.RESET}")
                process_result("Languages", results[0])
                process_result("Translation", results[1])
                process_result("Transcription", results[2])
                process_result("TTS Output", results[3])

                if all(not isinstance(r, Exception) for r in results):
                    self.test_results[test_name] = (
                        "Success",
                        "All operations completed",
                    )
                else:
                    failed = [
                        type(r).__name__ for r in results if isinstance(r, Exception)
                    ]
                    self.test_results[test_name] = (
                        "Failed",
                        f"Errors: {', '.join(failed)}",
                    )

            except Exception as e:
                print_error(f"Parallel operations error: {e}")
                self.test_results[test_name] = ("Failed", str(e))
                logging.error(f"Traceback:\n{traceback.format_exc()}")

    def test_version_management(self) -> None:
        test_name = "Version Management"
        print(f"{ConsoleColor.CYAN}\n{'VERSION MANAGEMENT':^60}{ConsoleColor.RESET}")

        print_success(
            f"Latest version: {ConsoleColor.YELLOW}{Versions.latest()}{ConsoleColor.RESET}"
        )
        print_success(
            f"Available versions: {ConsoleColor.GRAY}{[str(v) for v in Versions.all_versions()]}"
        )

        try:
            request = TranslationRequest(
                text="Hello world", source=Language.ENGLISH, target=Language.BAMBARA
            )
            result = self.sync_client.translation.translate(
                request=request, version=Versions.v1
            )
            print_success(
                f"Translation v1: '{ConsoleColor.YELLOW}{result.text}{ConsoleColor.RESET}'"
            )

            for version in [Versions.v1, Versions.v2]:
                transcription = self.sync_client.transcription.transcribe(
                    self.config.audio_file_path, version=version
                )
                handle_transcription_result(transcription, f"v{version.value}")

            tts_v1 = self.sync_client.tts.text_to_speech(
                request=TTSRequest(text=self.bambara_tts_text, speaker=1),
                output_file=f"tts_v1_{uuid4().hex}.wav",
                version=Versions.v1,
            )
            print_success(f"TTS v1: {ConsoleColor.BLUE}{tts_v1}{ConsoleColor.RESET}")

            tts_v2 = self.sync_client.tts.text_to_speech(
                request=TTSRequestV2(
                    text=self.bambara_tts_text,
                    description=f"{self.supported_speakers[0]} speaks with natural tone",
                ),
                output_file=f"tts_v2_{uuid4().hex}.wav",
                version=Versions.v2,
            )
            print_success(f"TTS v2: {ConsoleColor.BLUE}{tts_v2}{ConsoleColor.RESET}")

            self.test_results[test_name] = ("Success", "All version tests completed")

        except Exception as e:
            print_error(f"Version test error: {e}")
            self.test_results[test_name] = ("Failed", str(e))
            logging.error(f"Traceback:\n{traceback.format_exc()}")

    # ------------------------------
    # Main Execution
    # ------------------------------
    def run(self) -> None:
        print(f"\n{ConsoleColor.CYAN}{'=' * 60}{ConsoleColor.RESET}")
        print(
            f"{ConsoleColor.YELLOW}{'DJELIA SDK DEVELOPER COOKBOOK':^60}{ConsoleColor.RESET}"
        )
        print(f"{ConsoleColor.CYAN}{'=' * 60}{ConsoleColor.RESET}")

        logging.basicConfig(
            filename="djelia_cookbook.log",
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        if not self.validate_setup():
            return

        try:
            self.test_translation_sync()
            self.test_transcription_sync()
            self.test_tts_sync()
            self.test_streaming_transcription_sync()
            self.test_streaming_tts_sync()
            self.test_version_management()

            asyncio.run(self.test_translation_async())
            asyncio.run(self.test_transcription_async())
            asyncio.run(self.test_tts_async())
            asyncio.run(self.test_streaming_transcription_async())
            asyncio.run(self.test_streaming_tts_async())
            asyncio.run(self.test_parallel_operations())

            print_summary(self.test_results)

        except KeyboardInterrupt:
            print_error("Execution interrupted by user")
            self.test_results["Overall"] = ("Failed", "Interrupted")
            print_summary(self.test_results)
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            logging.error(f"Unhandled exception:\n{traceback.format_exc()}")
            self.test_results["Overall"] = ("Failed", "Runtime error")
            print_summary(self.test_results)
