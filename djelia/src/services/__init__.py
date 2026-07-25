from .audio import AsyncAudio, Audio
from .transcription import (AsyncTranscription, AsyncTranscriptions,
                            Transcription, Transcriptions)
from .translation import (AsyncTranslation, AsyncTranslations, Translation,
                          Translations)
from .tts import TTS, AsyncSpeech, AsyncTTS, Speech

__all__ = [
    # OpenAI-style resources
    "Translations",
    "AsyncTranslations",
    "Audio",
    "AsyncAudio",
    "Transcriptions",
    "AsyncTranscriptions",
    "Speech",
    "AsyncSpeech",
    # Deprecated aliases
    "Transcription",
    "AsyncTranscription",
    "Translation",
    "AsyncTranslation",
    "TTS",
    "AsyncTTS",
]
