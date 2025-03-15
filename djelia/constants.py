BASE_URL = "https://djelia.cloud"
API_KEY_HEADER = "x-api-key"
ENV_API_KEY = "DJELIA_API_KEY"

ENDPOINTS = {
    "translate": "/api/v1/models/translate",
    "supported_languages": "/api/v1/models/translate/supported-languages",
    "transcribe": "/api/v1/models/transcribe",
    "transcribe_stream": "/api/v1/models/transcribe/stream",
    "transcribe_v2": "/api/v2/models/transcribe",
    "transcribe_stream_v2": "/api/v2/models/transcribe/stream",
    "text_to_speech": "/api/v1/models/tts",
}

SUPPORTED_LANGUAGES = {
    "fr": "fra_Latn", 
    "en": "eng_Latn",  
    "bam": "bam_Latn",  
}

VALID_SPEAKER_IDS = [0, 1, 2, 3, 4]
DEFAULT_SPEAKER_ID = 1