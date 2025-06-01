from typing import Any

from djelia.utils.exceptions import (APIError, AuthenticationError,
                                     DjeliaError, ValidationError)


class ExceptionMessage:
    messages: dict[int, str] = {
        401: "Invalid or expired API key",
        403: "Forbidden: You do not have permission to access this resource",
        404: "Resource not found",
        422: "Validation error",
    }
    default: str = "API error {}"
    failed: str = "Request failed: {}"


class CodeStatusExceptions:
    exceptions: dict[int, Any] = {
        401: AuthenticationError,
        403: APIError,
        404: APIError,
        422: ValidationError,
    }
    default = DjeliaError


def api_exception(code: int, error: Exception) -> Exception:
    return CodeStatusExceptions.exceptions.get(code, APIError)(
        ExceptionMessage.messages.get(code, ExceptionMessage.default.format(str(error)))
    )


def general_exception(error: Exception) -> Exception:
    return CodeStatusExceptions.default(ExceptionMessage.failed.format(str(error)))
