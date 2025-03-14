from .client import Djelia
from .constants import (
    SUPPORTED_LANGUAGES,
    VALID_SPEAKER_IDS
)

from .exceptions import (
    DjeliaError,
    AuthenticationError,
    ValidationError,
    APIError,
    LanguageError,
    SpeakerError,
    AudioFormatError
)

__version__ = "0.1.0"

__all__ = [
    'Djelia',
    'SUPPORTED_LANGUAGES',
    'VALID_SPEAKER_IDS'
    ]