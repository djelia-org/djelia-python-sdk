## API Reference

The Djelia Python SDK interacts with the Djelia API at `https://djelia.cloud/api/v{version}/models/`. Below are the key endpoints used by the SDK.

### Authentication
- **Header**: `x-api-key: <your_api_key>`
- **Environment Variable**: `DJELIA_API_KEY`

### Endpoints

| Endpoint | Method | Description | SDK Method |
|----------|--------|-------------|------------|
| `/api/v{version}/models/translate/supported-languages` | GET | List supported languages | `translation.get_supported_languages()` |
| `/api/v{version}/models/translate` | POST | Translate text | `translation.translate()` |
| `/api/v{version}/models/transcribe` | POST | Transcribe audio | `transcription.transcribe(stream=False)` |
| `/api/v{version}/models/transcribe/stream` | POST | Stream transcription | `transcription.transcribe(stream=True)` |
| `/api/v{version}/models/tts` | POST | Generate TTS audio | `tts.text_to_speech(stream=False)` |
| `/api/v{version}/models/tts/stream` | POST | Stream TTS audio | `tts.text_to_speech(stream=True)` |

### Rate Limits
- Contact [support@djelia.cloud](mailto:support@djelia.cloud) for rate limit details.
- The SDK uses `tenacity` for retries (3 attempts with exponential backoff).

### Error Responses
- **401**: Invalid or expired API key (`AuthenticationError`).
- **403**: Forbidden access (`APIError`).
- **404**: Resource not found (`APIError`).
- **422**: Validation error (`ValidationError`).