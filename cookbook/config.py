import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str | None = None
    audio_file_path: str = "audio.wav"
    max_stream_segments: int = 3
    max_stream_chunks: int = 5

    @classmethod
    def load(cls) -> "Config":
        load_dotenv()
        return cls(
            api_key=os.environ.get("DJELIA_API_KEY"),
            audio_file_path=os.environ.get("TEST_AUDIO_FILE", "audio.wav"),
        )
