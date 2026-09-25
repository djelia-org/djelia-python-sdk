from unittest.mock import MagicMock, patch

from djelia import Djelia

VALID_API_KEY = "12345678-1234-1234-1234-123456789012"


def test_custom_base_url_is_used_to_build_the_request_url():
    """
    A client configured with a custom base_url must send its requests to that host.

    This guards against the endpoint being built from a hardcoded prefix instead of
    the configured setting, which was the bug reported in issue #17.
    """
    client = Djelia(api_key=VALID_API_KEY, base_url="https://custom.example.com")

    with patch("djelia.src.client.client.requests.request") as mock_request:
        mock_request.return_value = MagicMock(status_code=200, json=lambda: [])

        client.translations.list_languages()

        called_url = mock_request.call_args.args[1]
        assert called_url.startswith("https://custom.example.com/")
