from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_url: str = Field(validation_alias="BASE_URL", default="https://djelia.cloud")
    djelia_api_key: str = Field(validation_alias="DJELIA_API_KEY")
    valid_speaker_ids: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4])
    valid_tts_v2_speakers: List[str] = Field(
        default_factory=lambda: ["Moussa", "Sekou", "Seydou"]
    )
    default_speaker_id: int = 1
