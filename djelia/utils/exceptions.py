class DjeliaError(Exception):
    """Base exception for all Djelia client errors"""

    pass


class AuthenticationError(DjeliaError):
    """Exception raised for authentication errors"""

    pass


class ValidationError(DjeliaError):
    """Exception raised for validation errors"""

    pass


class APIError(DjeliaError):
    """Exception raised for API errors"""

    def __init__(self, status_code, message, *args):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error ({status_code}): {message}", *args)


class LanguageError(ValidationError):
    """Exception raised for unsupported languages"""

    pass


class SpeakerError(ValidationError):
    """Exception raised for invalid speaker IDs"""

    pass
