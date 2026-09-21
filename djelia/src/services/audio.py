from djelia.src.services.transcription import AsyncTranscriptions, Transcriptions
from djelia.src.services.tts import AsyncSpeech, Speech


class Audio:
    """OpenAI-style audio namespace: ``client.audio.transcriptions`` and
    ``client.audio.speech``."""

    def __init__(self, client):
        self.transcriptions = Transcriptions(client)
        self.speech = Speech(client)


class AsyncAudio:
    """OpenAI-style async audio namespace: ``client.audio.transcriptions`` and
    ``client.audio.speech``."""

    def __init__(self, client):
        self.transcriptions = AsyncTranscriptions(client)
        self.speech = AsyncSpeech(client)
