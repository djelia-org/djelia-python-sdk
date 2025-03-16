from .client import Djelia, AsyncDjelia
from .constants import djelia_config


SUPPORTED_LANGUAGES = djelia_config.SUPPORTED_LANGUAGES
VALID_SPEAKER_IDS = djelia_config.VALID_SPEAKER_IDS

from .exceptions import (
    DjeliaError,
    AuthenticationError,
    ValidationError,
    APIError,
    LanguageError,
    SpeakerError,
    AudioFormatError
)

__version__ = "0.2.0"

__all__ = [
    'Djelia',
    'AsyncDjelia',
    'SUPPORTED_LANGUAGES',
    'VALID_SPEAKER_IDS'
]

    # let's close those component
    # 'DjeliaError',
    # 'AuthenticationError',
    # 'ValidationError',
    # 'APIError',
    # 'LanguageError',
    # 'SpeakerError',
    # 'AudioFormatError'