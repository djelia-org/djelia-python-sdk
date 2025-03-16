# Djelia Python Client

A simple Python client for the Djelia API, providing language services for Bambara and other African languages.

## Installation

```bash
pip install git+https://github.com/djelia-org/djelia-python-client
```

## Quick Start

### Authentication

```python
from djelia import Djelia

# Using API key directly
client = Djelia(api_key="your_api_key")

# Or use environment variable
# export DJELIA_API_KEY=your_api_key
client = Djelia()
```

### Translation

Translate text between supported languages:

```python
result = client.translate(
    text="Hello, how are you?", 
    source="en",  # English
    target="bam"  # Bambara
)
print(result["text"])
```

### Transcription

Convert speech to text from audio files:

```python
# Basic transcription
result = client.transcribe("audio_file.mp3")

# With timestamps (version 2)
result = client.transcribe("audio_file.mp3", version=2)
for segment in result:
    print(f"{segment['text']}")

# With French translation
result = client.transcribe("audio_file.mp3", translate_to_french=True)
```

### Streaming Transcription

Process audio in real-time:

```python
for segment in client.stream_transcribe("audio_file.mp3"):
    print(segment["text"])
```

### Text-to-Speech

Convert text to natural-sounding speech:

```python
# Generate audio and save to file
client.text_to_speech(
    "Text to convert to speech",
    speaker=1,  # Choose voice (0-4)
    output_file="output.mp3"
)

# Get audio as bytes
audio_bytes = client.text_to_speech("Hello world")
```

## Async Support

For high-performance applications, use the async client:

```python
from djelia import AsyncDjelia
import asyncio

async def main():
    async with AsyncDjelia(api_key="your_api_key") as client:
        # All methods are the same, just use "await"
        result = await client.translate("Hello", "en", "fr")
        print(result["text"])
        
        # Streaming has a slightly different syntax
        async for segment in client.stream_transcribe("audio.mp3"):
            print(segment["text"])

asyncio.run(main())
```

### Parallel Processing

Run multiple operations simultaneously for better performance:

```python
async def main():
    async with AsyncDjelia(api_key="your_api_key") as client:
        # Run tasks in parallel
        results = await asyncio.gather(
            client.translate("Hello", "en", "bam"),
            client.get_supported_languages(),
            client.text_to_speech("Aw ni ce", output_file="greeting.wav")
        )
        
        # Access results
        translation, languages, audio_path = results

asyncio.run(main())
```

## Supported Languages

Currently supports:
- English (en)
- French (fr)
- Bambara (bam)

Check available languages:
```python
languages = client.get_supported_languages()
```

## Error Handling

Handle API errors gracefully:

```python
from djelia import Djelia, DjeliaError

try:
    client = Djelia(api_key="your_api_key")
    result = client.translate("Hello", "en", "bam")
except DjeliaError as e:
    print(f"API error: {e}")
```

## Support

Need help? Contact: support@djelia.cloud