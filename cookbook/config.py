import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# The Bambara greeting reused across every TTS test.
DEFAULT_TTS_TEXT = "Aw ni ce, i ka kɛnɛ wa?"
DEFAULT_SPEAKERS = ["Moussa", "Sekou", "Seydou"]


@dataclass
class Config:
    """Runtime configuration for the Djelia SDK test suite."""

    api_key: str | None = None
    audio_file_path: str = "audio.wav"
    output_dir: str = "cookbook_output"
    keep_audio: bool = False
    max_stream_segments: int = 3
    max_stream_chunks: int = 5
    tts_text: str = DEFAULT_TTS_TEXT
    speakers: list[str] = field(default_factory=lambda: list(DEFAULT_SPEAKERS))

    @classmethod
    def load(cls) -> "Config":
        load_dotenv()
        return cls(
            api_key=os.environ.get("DJELIA_API_KEY"),
            audio_file_path=os.environ.get("TEST_AUDIO_FILE", "audio.wav"),
        )
