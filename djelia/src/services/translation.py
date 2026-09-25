import warnings

from djelia.models import (
    DjeliaRequest,
    Language,
    SupportedLanguageSchema,
    TranslationRequest,
    TranslationResponse,
    Versions,
)


class Translations:
    """OpenAI-style translation resource: ``client.translations``."""

    def __init__(self, client):
        self.client = client

    def list_languages(self) -> list[SupportedLanguageSchema]:
        response = self.client._make_request(
            method=DjeliaRequest.get_supported_languages.method,
            endpoint=DjeliaRequest.get_supported_languages.endpoint.format(
                Versions.v1.value
            ),
        )
        return [SupportedLanguageSchema(**lang) for lang in response.json()]

    def create(
        self,
        *,
        text: str,
        source: Language | str,
        target: Language | str,
        model: Versions | int | str = Versions.v1,
    ) -> TranslationResponse:
        version = Versions.from_value(model)
        request = TranslationRequest(text=text, source=source, target=target)
        response = self.client._make_request(
            method=DjeliaRequest.translate.method,
            endpoint=DjeliaRequest.translate.endpoint.format(version.value),
            json=request.dict(),
        )
        return TranslationResponse(**response.json())


class AsyncTranslations:
    """OpenAI-style async translation resource: ``client.translations``."""

    def __init__(self, client):
        self.client = client

    async def list_languages(self) -> list[SupportedLanguageSchema]:
        data = await self.client._make_request(
            method=DjeliaRequest.get_supported_languages.method,
            endpoint=DjeliaRequest.get_supported_languages.endpoint.format(
                Versions.v1.value
            ),
        )
        return [SupportedLanguageSchema(**lang) for lang in data]

    async def create(
        self,
        *,
        text: str,
        source: Language | str,
        target: Language | str,
        model: Versions | int | str = Versions.v1,
    ) -> TranslationResponse:
        version = Versions.from_value(model)
        request = TranslationRequest(text=text, source=source, target=target)
        data = await self.client._make_request(
            method=DjeliaRequest.translate.method,
            endpoint=DjeliaRequest.translate.endpoint.format(version.value),
            json=request.dict(),
        )
        return TranslationResponse(**data)


class Translation:
    """Deprecated. Use ``client.translations`` instead."""

    def __init__(self, client):
        self.client = client

    def get_supported_languages(self) -> list[SupportedLanguageSchema]:
        warnings.warn(
            "Translation.get_supported_languages() is deprecated; "
            "use client.translations.list_languages() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.client.translations.list_languages()

    def translate(
        self,
        request: TranslationRequest,
        version: Versions | None = Versions.v1,
    ) -> TranslationResponse:
        warnings.warn(
            "Translation.translate() is deprecated; "
            "use client.translations.create(text=..., source=..., target=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.client.translations.create(
            text=request.text,
            source=request.source,
            target=request.target,
            model=version,
        )


class AsyncTranslation:
    """Deprecated. Use ``client.translations`` instead."""

    def __init__(self, client):
        self.client = client

    async def get_supported_languages(self) -> list[SupportedLanguageSchema]:
        warnings.warn(
            "AsyncTranslation.get_supported_languages() is deprecated; "
            "use client.translations.list_languages() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.client.translations.list_languages()

    async def translate(
        self,
        request: TranslationRequest,
        version: Versions | None = Versions.v1,
    ) -> TranslationResponse:
        warnings.warn(
            "AsyncTranslation.translate() is deprecated; "
            "use client.translations.create(text=..., source=..., target=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return await self.client.translations.create(
            text=request.text,
            source=request.source,
            target=request.target,
            model=version,
        )
