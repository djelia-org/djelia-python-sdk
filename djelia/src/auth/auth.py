from djelia.models.models import ErrorsMessage
from djelia.utils.utils import is_valid_uuid


class Auth:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

        if not is_valid_uuid(self.api_key):
            raise ValueError(ErrorsMessage.api_key_missing)

    def get_headers(self):
        return {"x-api-key": self.api_key}
