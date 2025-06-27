from djelia.models import (DjeliaRequest, SupportedLanguageSchema,
                           TranslationRequest, TranslationResponse, Versions)


class Translation:
    def __init__(self, client):
        self.client = client

    def get_supported_languages(self) -> list[SupportedLanguageSchema]:
        response = self.client._make_request(
            method=DjeliaRequest.get_supported_languages.method,
            endpoint=DjeliaRequest.get_supported_languages.endpoint.format(
                Versions.v1.value
            ),
        )
        return [SupportedLanguageSchema(**lang) for lang in response.json()]

    def translate(
        self,
        request: TranslationRequest,
        version: Versions | None = Versions.v1.value,
    ) -> TranslationResponse:
        data = request.dict()
        response = self.client._make_request(
            method=DjeliaRequest.translate.method,
            endpoint=DjeliaRequest.translate.endpoint.format(version.value),
            json=data,
        )
        return TranslationResponse(**response.json())


class AsyncTranslation:
    def __init__(self, client):
        self.client = client

    async def get_supported_languages(self) -> list[SupportedLanguageSchema]:
        data = await self.client._make_request(
            method=DjeliaRequest.get_supported_languages.method,
            endpoint=DjeliaRequest.get_supported_languages.endpoint.format(
                Versions.v1.value
            ),
        )
        return [SupportedLanguageSchema(**lang) for lang in data]

    async def translate(
        self, request: TranslationRequest, version: Versions | None = Versions.v1
    ) -> TranslationResponse:
        request_data = request.dict()
        data = await self.client._make_request(
            method=DjeliaRequest.translate.method,
            endpoint=DjeliaRequest.translate.endpoint.format(version.value),
            json=request_data,
        )
        return TranslationResponse(**data)
