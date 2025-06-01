# from djelia.config.settings import API_KEY_HEADER, ENV_API_KEY
import os

from djelia.models.models import API_KEY_HEADER, ENV_API_KEY, ErrorsMessage


class Auth:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get(ENV_API_KEY)

        if not self.api_key:
            raise ValueError(ErrorsMessage.api_key_missing)

    def get_headers(self):
        return {API_KEY_HEADER: self.api_key}
