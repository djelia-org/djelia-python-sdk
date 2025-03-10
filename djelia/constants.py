BASE_URL = "https://djelia.cloud/api/v1"
API_KEY_HEADER = "x-api-key"
ENV_API_KEY = "DJELIA_API_KEY"

ENDPOINTS = {
    "translate": "/models/translate",
    "supported_languages": "/models/translate/supported-languages",
    "transcribe": "/models/transcribe",
    "transcribe_stream": "/models/transcribe/stream",
    "text_to_speech": "/models/tts",
}

SUPPORTED_LANGUAGES = {
    "fr": "fra_Latn", 
    "en": "eng_Latn",  
    "bam": "bam_Latn",  
}

VALID_SPEAKER_IDS = [0, 1, 2, 3, 4]
DEFAULT_SPEAKER_ID = 1