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

__version__ = "0.2.0"

__all__ = [
    'Djelia'
]

# let's explose only the main client, know that this is a quick implementation so we will come back 

    # 'SUPPORTED_LANGUAGES',
    # 'VALID_SPEAKER_IDS',
    # 'DjeliaError',
    # 'AuthenticationError',
    # 'ValidationError',
    # 'APIError',
    # 'LanguageError',
    # 'SpeakerError',
    # 'AudioFormatError'