## API Reference

The Djelia Python SDK interacts with the Djelia API at `https://api.djelia.cloud/v{version}/models/`. Below are the key endpoints used by the SDK.

### Authentication
- **Header**: `x-api-key: <your_api_key>`
- **Environment Variable**: `DJELIA_API_KEY`

### Endpoints

| Endpoint | Method | Description | SDK Method |
|----------|--------|-------------|------------|
| `/v{version}/models/translate/supported-languages` | GET | List supported languages | `translations.list_languages()` |
| `/v{version}/models/translate` | POST | Translate text | `translations.create()` |
| `/v{version}/models/transcribe` | POST | Transcribe audio | `audio.transcriptions.create(stream=False)` |
| `/v{version}/models/transcribe/stream` | POST | Stream transcription | `audio.transcriptions.create(stream=True)` |
| `/v{version}/models/tts` | POST | Generate TTS audio | `audio.speech.create(stream=False)` |
| `/v{version}/models/tts/stream` | POST | Stream TTS audio | `audio.speech.create(stream=True)` |

> The pre-`2.0` methods (`translation.translate()`, `transcription.transcribe()`, `tts.text_to_speech()`) still work but are deprecated and emit a `DeprecationWarning`.

### Rate Limits
- Contact [support@djelia.cloud](mailto:support@djelia.cloud) for rate limit details.
- The SDK uses `tenacity` for retries (3 attempts with exponential backoff).

### Error Responses
- **401**: Invalid or expired API key (`AuthenticationError`).
- **403**: Forbidden access (`APIError`).
- **404**: Resource not found (`APIError`).
- **422**: Validation error (`ValidationError`).