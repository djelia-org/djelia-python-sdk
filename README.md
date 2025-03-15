# Djelia Python client

Python client for Djelia API,  linguistic models for bambara.

## Installation

```bash
  pip install git+https://github.com/djelia-org/djelia-python-client
```

## Authentication

```python
# Option 1: Direct API key
from djelia import Djelia
client = Djelia(api_key="your_api_key")

# Option 2: Environment variable
# export DJELIA_API_KEY=your_api_key
client = Djelia()
```

## Features

### Translation

```python
# English to Bambara
translation = client.translate(
    text="Hello, how are you doing today?", 
    source="en", 
    target="bam"
)
print(translation["text"])  
```

### Transcription

```python
# V1 Transcription (default)
result = client.transcribe("audio_file.wav")
for segment in result:
    print(f"{segment['text']} ({segment['start']} - {segment['end']})")

# V2 Transcription 
result_v2 = client.transcribe("audio_file.wav", version=2)
for segment in result_v2:
    print(f"{segment['text']} ({segment['start']} - {segment['end']})")

# Translate to French
french_result = client.transcribe("audio_file.wav", translate_to_french=True)
print(french_result["text"])
```

### Streaming Transcription

```python
# V1 Streaming
for segment in client.stream_transcribe("audio_file.wav"):
    print(f"{segment['text']} ({segment['start']} - {segment['end']})")

# V2 Streaming
for segment in client.stream_transcribe("audio_file.wav", version=2):
    print(f"{segment['text']} ({segment['start']} - {segment['end']})")
```

### Text-to-Speech

```python
# Return audio bytes
audio_data = client.text_to_speech("Aw ni ce")

# Save to file
audio_path = client.text_to_speech("Aw ni ce", speaker=1, output_file="greeting.wav")
```

### Language Support

```python
languages = client.get_supported_languages()
# [{'code': 'fra_Latn', 'name': 'French'}, 
#  {'code': 'eng_Latn', 'name': 'English'}, 
#  {'code': 'bam_Latn', 'name': 'Bambara'}]
```

## Support

Email: [support@djelia.cloud](mailto:support@djelia.cloud)