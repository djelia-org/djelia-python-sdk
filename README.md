# <h1 style="color:#00FFFF;"> Djelia Python SDK Workshop
Hey there! Welcome to this fun and practical workshop on using the Djelia Python SDK. Whether you're translating between African languages, transcribing audio with realtime streaming, or generating natural sounding speech, this guide has got you covered. We'll walk through installing the SDK, setting up clients, and performing some cool operations like multi language translation, audio transcription, and text-to-speech generation. I've added a sprinkle of humor to keep things light because who said coding can't be fun, right? Let's dive in!

## <h3 style="color:#00FFFF;"> Table of Contents

1. [Installation](#installation)
2. [Client Initialization](#client-initialization)
   - 2.1 [API Key Loading](#api-key-loading)
   - 2.2 [Synchronous Client](#synchronous-client)
   - 2.3 [Asynchronous Client](#asynchronous-client)
3. [Operations](#operations)
   - 3.1 [Translation](#translation)
     - 3.1.1 [Get Supported Languages](#get-supported-languages)
     - 3.1.2 [Translate Text](#translate-text)
   - 3.2 [Transcription](#transcription)
     - 3.2.1 [Basic Transcription](#basic-transcription)
     - 3.2.2 [Streaming Transcription](#streaming-transcription)
     - 3.2.3 [French Translation](#french-translation)
   - 3.3 [Text-to-Speech (TTS)](#text-to-speech-tts)
     - 3.3.1 [TTS v1 with Speaker ID](#tts-v1-with-speaker-id)
     - 3.3.2 [TTS v2 with Natural Descriptions](#tts-v2-with-natural-descriptions)
     - 3.3.3 [Streaming TTS](#streaming-tts)
   - 3.4 [Version Management](#version-management)
   - 3.5 [Parallel Operations](#parallel-operations)
4. [Error Handling](#error-handling)
5. [Explore the Djelia SDK Cookbook](#explore-the-djelia-sdk-cookbook)

## <h3 style="color:#00FFFF;"> Installation

Let's kick things off by installing the Djelia Python SDK with  one of those magical commands. Run it in your terminal, and you're good to go!

```bash
    pip install djelia
```


Install the Djelia Python SDK directly from GitHub:
```bash
    pip install git+https://github.com/djelia/djelia-python-sdk.git
```

Alternatively, use uv for faster dependency resolution:


```bash
    uv pip install djelia
```


```bash
    uv pip install git+https://github.com/djelia/djelia-python-sdk.git
```

<span style="color:red">Note:</span> A PyPI package (pip install djelia) is coming soon stay tuned!


## <h3 style="color:#00FFFF;"> Client Initialization

Before we can do anything fancy, we need to set up our clients. This involves loading our API key and initializing both synchronous and asynchronous clients. Here's how:

## <h3 style="color:#00FFFF;"> API Key Loading

First, grab your API key from a `.env` file it's the safest way to keep your secrets, well, secret! If you don't have one yet, head to the Djelia dashboard and conjure one up.

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ.get("DJELIA_API_KEY")

# Alternatively: api_key = "your_api_key_here" (but shh, that's not safe!)

# Specify your audio file for transcription tests
audio_file_path = os.environ.get("TEST_AUDIO_FILE", "audio.wav")
```

> <span style="color:red;"> **Note:** </span> Ensure your audio file (e.g., `audio.wav`) exists at the specified path. Set `TEST_AUDIO_FILE` in your `.env` file if using a custom path:
> ```bash
> echo "TEST_AUDIO_FILE=/path/to/your/audio.wav" >> .env
> ```
> Without a valid audio file, transcription operations will fail. That not what you want right 😂


<h3 style="color:#00FFFF;">Synchronous Client</h3>



For those who like to take things one step at a time, here's how to set up the synchronous client:

```python
from djelia import Djelia

djelia_client = Djelia(api_key=api_key)

# if DJELIA_API_KEY is already set you can just do : (yes I know I'm making your life easy 😂)
djelia_client = Djelia()

```

## <h3 style="color:#00FFFF;"> Asynchronous Client

If you're ready to live on the async edge, initialize the asynchronous client like this:

```python
from djelia import DjeliaAsync

djelia_async_client = DjeliaAsync(api_key=api_key)

# if DJELIA_API_KEY is already set you can just do : (again easy life 😂)

djelia_async_client = DjeliaAsync()
```

## <h3 style="color:#00FFFF;"> Operations 🇲🇱

<span style="color:gold;"> Now for the fun part let's do stuff with the Djelia API! We'll cover translating between African languages, transcribing audio (with streaming!), and generating natural speech, with examples for both synchronous and asynchronous approaches.</span> <span style="color:red;"> Yes, yes, let's do it ❤️‍🔥! 


## <h3 style="color:#00FFFF;"> Translation

Let's unlock the power of multilingual communication! 
## <h3 style="color:#00FFFF;"> Get Supported Languages

First, let's see what languages we can work with.

## <h3 style="color:#00FFFF;"> Synchronous

Simple and straightforward get your supported languages and print them:

```python
supported_languages = djelia_client.translation.get_supported_languages()
for lang in supported_languages:
    print(f"{lang.name}: {lang.code}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

For the async fans, here's how to fetch supported languages. Don't forget to run it with asyncio:

```python
import asyncio

async def get_languages_test():
    async with djelia_async_client as client:
        supported_languages = await client.translation.get_supported_languages()
        for lang in supported_languages:
            print(f"{lang.name}: {lang.code}")

asyncio.run(get_languages_test())
```

## <h3 style="color:#00FFFF;"> Translate Text

Let's translate some text between beautiful 🇲🇱 languages and others. Feel free to try different language combinations!

```python
from djelia.models import TranslationRequest, Language, Versions

request = TranslationRequest(
    text="Hello, how are you today?",
    source=Language.ENGLISH,
    target=Language.BAMBARA
)
```

## <h3 style="color:#00FFFF;"> Synchronous

Create that translation and see what you get:

```python
from djelia.models import TranslationResponse

try:
    response_sync: TranslationResponse = djelia_client.translation.translate(request=request, version=Versions.v1)
    print(f"Original: {request.text}")
    print(f"Translation: {response_sync.text}")
except Exception as e:
    print(f"Translation error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

Async translation because why wait around? Let's do it bro !

```python
async def translate_async():
    async with djelia_async_client as client:
        try:
            response_async: TranslationResponse = await client.translation.translate(request=request, version=Versions.v1)
            print(f"Original: {request.text}")
            print(f"Translation: {response_async.text}")
            return response_async
        except Exception as e:
            print(f"Translation error: {e}")

asyncio.run(translate_async())
```

## <h3 style="color:#00FFFF;"> Transcription

Time to turn audio into text with timestamps and everything!

## <h3 style="color:#00FFFF;"> Basic Transcription

Let's transcribe some audio files. Make sure you have an audio file ready check <span style="color:red;"> audio_file_path</span>.

## <h3 style="color:#00FFFF;"> Synchronous

```python
from djelia.models import Versions

try:
    transcription = djelia_client.transcription.transcribe(
        audio_file=audio_file_path,
        version=Versions.v2
    )
    print(f"Transcribed {len(transcription)} segments:")
    for segment in transcription:
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")
except Exception as e:
    print(f"Transcription error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

For the async enthusiasts: (like me, I ❤️ it)

```python
async def transcribe_async():
    async with djelia_async_client as client:
        try:
            transcription = await client.transcription.transcribe(
                audio_file=audio_file_path,
                version=Versions.v2
            )
            print(f"Transcribed {len(transcription)} segments:")
            for segment in transcription:
                print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")
        except Exception as e:
            print(f"Transcription error: {e}")

asyncio.run(transcribe_async())
```

## <h3 style="color:#00FFFF;"> Streaming Transcription

Want realtime results? Let's stream that transcription! <span style="color:gold">This is really important of live applications</span>

## <h3 style="color:#00FFFF;"> Synchronous

```python
print("Streaming transcription (showing first 3 segments)...")
segment_count = 0

try:
    for segment in djelia_client.transcription.transcribe(
        audio_file=audio_file_path,
        stream=True,
        version=Versions.v2
    ):
        segment_count += 1
        print(f"Segment {segment_count}: [{segment.start:.2f}s]: {segment.text}")
        
        if segment_count >= 3:  # Just showing first 3 for demo
            print("...and more segments!")
            break
except Exception as e:
    print(f"Streaming transcription error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

Async streaming because realtime is awesome: (bro, I'm telling you,  one second is a lot)

```python
async def stream_transcribe_async():
    async with djelia_async_client as client:
        try:
            stream = await client.transcription.transcribe(
                audio_file=audio_file_path,
                stream=True,
                version=Versions.v2
            )
            segment_count = 0
            async for segment in stream:
                segment_count += 1
                print(f"Segment {segment_count}: [{segment.start:.2f}s]: {segment.text}")
                
                if segment_count >= 3:  # Just showing first 3 for demo
                    print("...and more segments!")
                    break
        except Exception as e:
            print(f"Streaming transcription error: {e}")

asyncio.run(stream_transcribe_async())
```

## <h3 style="color:#00FFFF;"> French Translation

Want to transcribe and translate to French in one go? We've got you covered!

## <h3 style="color:#00FFFF;"> Synchronous

```python
try:
    french_transcription = djelia_client.transcription.transcribe(
        audio_file=audio_file_path,
        translate_to_french=True,
        version=Versions.v2
    )
    print(f"French translation: {french_transcription.text}")
except Exception as e:
    print(f"French transcription error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

```python
async def transcribe_french_async():
    async with djelia_async_client as client:
        try:
            french_transcription = await client.transcription.transcribe(
                audio_file=audio_file_path,
                translate_to_french=True,
                version=Versions.v2
            )
            print(f"French translation: {french_transcription.text}")
        except Exception as e:
            print(f"French transcription error: {e}")

asyncio.run(transcribe_french_async())
```

## <h3 style="color:#00FFFF;"> Text-to-Speech (TTS)

Let's make some beautiful voices! Choose between numbered speakers or describe exactly how you want it to sound.

## <h3 style="color:#00FFFF;"> TTS v1 with Speaker ID

Classic approach with speaker IDs (0-4). Simple and effective!

```python
from djelia.models import TTSRequest

tts_request_v1 = TTSRequest(
    text="Aw ni ce, i ka kɛnɛ wa?",  # "Hello, how are you?" in Bambara
    speaker=1  # Choose from 0, 1, 2, 3, or 4
)
```

## <h3 style="color:#00FFFF;"> Synchronous

Generate that audio and save it:

```python
try:
    audio_file_v1 = djelia_client.tts.text_to_speech(
        request=tts_request_v1,
        output_file="hello_v1.wav",
        version=Versions.v1
    )
    print(f"Audio saved to: {audio_file_v1}")
except Exception as e:
    print(f"TTS v1 error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

Async audio generation:

```python
async def generate_audio_v1_async():
    async with djelia_async_client as client:
        try:
            audio_file_v1 = await client.tts.text_to_speech(
                request=tts_request_v1,
                output_file="hello_v1_async.wav",
                version=Versions.v1
            )
            print(f"Audio saved to: {audio_file_v1}")
        except Exception as e:
            print(f"TTS v1 error: {e}")

asyncio.run(generate_audio_v1_async())
```

## <h3 style="color:#00FFFF;"> TTS v2 with Natural Descriptions

This is where it gets fun! Describe exactly how you want the voice to sound, but make sure to include one of the supported speakers: Moussa, Sekou, or Seydou.

```python
from djelia.models import TTSRequestV2

tts_request_v2 = TTSRequestV2(
    text="Aw ni ce, i ka kɛnɛ wa?",
    description="Seydou speaks with a warm, welcoming tone",  # Must include Moussa, Sekou, or Seydou
    chunk_size=1.0  # Control speech pacing (0.1 - 2.0)
)
```

> <span style="color:red"> **Note:** </span> The description field must include one of the supported speakers. For example, "Moussa speaks with a warm tone" is valid, but "Natural tone" will raise an error. 

## <h3 style="color:#00FFFF;"> Synchronous

Create natural sounding speech:

```python
try:
    audio_file_v2 = djelia_client.tts.text_to_speech(
        request=tts_request_v2,
        output_file="hello_v2.wav",
        version=Versions.v2
    )
    print(f"Natural audio saved to: {audio_file_v2}")
except Exception as e:
    print(f"TTS v2 error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

Async natural speech generation:

```python
async def generate_natural_audio_async():
    async with djelia_async_client as client:
        try:
            audio_file_v2 = await client.tts.text_to_speech(
                request=tts_request_v2,
                output_file="hello_v2_async.wav",
                version=Versions.v2
            )
            print(f"Natural audio saved to: {audio_file_v2}")
        except Exception as e:
            print(f"TTS v2 error: {e}")

asyncio.run(generate_natural_audio_async())
```

## <h3 style="color:#00FFFF;"> Streaming TTS

Realtime audio generation! Get chunks as they're created <span style="color:red">(v2 only)</span>.

```python
streaming_tts_request = TTSRequestV2(
    text="An filɛ ni ye yɔrɔ minna ni an ye an sigi ka a layɛ yala an bɛ ka baara min kɛ ɛsike a kɛlen don ka Ɲɛ wa, ...............", # a very long text 
    description="Seydou speaks clearly and naturally",
    chunk_size=1.0
)
```

> <span style="color:red">**Note:**</span> By default, the SDK may process multiple chunks (e.g., up to 5 in some configurations). This example limits to 5 chunks for consistency, but you can adjust the limit based on your application needs.

## <h3 style="color:#00FFFF;"> Synchronous

Stream that audio generation: (this is handsome)

```python
print("Streaming TTS generation...")
chunk_count = 0
total_bytes = 0
max_chunks = 5

try:
    for chunk in djelia_client.tts.text_to_speech(
        request=streaming_tts_request,
        output_file="streamed_audio.wav",
        stream=True,
        version=Versions.v2
    ):
        chunk_count += 1
        total_bytes += len(chunk)
        print(f"Chunk {chunk_count}: {len(chunk)} bytes")
        
        if chunk_count >= max_chunks:
            print(f"...and more chunks! (Total so far: {total_bytes} bytes)")
            break
except Exception as e:
    print(f"Streaming TTS error: {e}")
```

## <h3 style="color:#00FFFF;"> Asynchronous

Async streaming TTS because realtime is the future (oops, actually it's today 😂):

```python
async def stream_tts_async():
    async with djelia_async_client as client:
        try:
            stream = await client.tts.text_to_speech(
                request=streaming_tts_request,
                output_file="streamed_audio_async.wav",
                stream=True,
                version=Versions.v2
            )
            chunk_count = 0
            total_bytes = 0
            max_chunks = 5
            
            async for chunk in stream:
                chunk_count += 1
                total_bytes += len(chunk)
                print(f"Chunk {chunk_count}: {len(chunk)} bytes")
                
                if chunk_count >= max_chunks:
                    print(f"...and more chunks! (Total so far: {total_bytes} bytes)")
                    break
        except Exception as e:
            print(f"Streaming TTS error: {e}")

asyncio.run(stream_tts_async())
```

## <h3 style="color:#00FFFF;"> Version Management

The SDK supports multiple API versions (v1, v2) via the Versions enum. Use `Versions.latest()` to get the latest version or `Versions.all_versions()` to list available versions.

```python
from djelia.models import Versions

print(f"Latest version: {Versions.latest()}")
print(f"Available versions: {[str(v) for v in Versions.all_versions()]}")

# Use specific version
try:
    transcription = djelia_client.transcription.transcribe(
        audio_file=audio_file_path,
        version=Versions.v2
    )
    print(f"Transcribed {len(transcription)} segments")
except Exception as e:
    print(f"Transcription error: {e}")
```

## <h3 style="color:#00FFFF;"> Parallel Operations

Run multiple API operations concurrently using `asyncio.gather` with the async client. This is great for performance in applications needing simultaneous translations, transcriptions, or TTS generation.

```python
import asyncio
from djelia.models import TranslationRequest, Language, TTSRequestV2, Versions

async def parallel_operations():
    async with DjeliaAsync(api_key=api_key) as client:
        try:
            translation_request = TranslationRequest(
                text="Hello", source=Language.ENGLISH, target=Language.BAMBARA
            )
            tts_request = TTSRequestV2(
                text="Aw ni ce, i ka kɛnɛ wa?",
                description="Moussa speaks with a clear tone",
                chunk_size=1.0
            )
            
            results = await asyncio.gather(
                client.translation.translate(translation_request, version=Versions.v1),
                client.transcription.transcribe(audio_file_path, version=Versions.v2),
                client.tts.text_to_speech(tts_request, output_file="parallel_tts.wav", version=Versions.v2),
                return_exceptions=True
            )
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Operation {i+1} failed: {result}")
                else:
                    print(f"Operation {i+1} succeeded: {type(result).__name__}")
        except Exception as e:
            print(f"Parallel operations error: {e}")

asyncio.run(parallel_operations())
```

## <h3 style="color:#00FFFF;"> Error Handling

The Djelia SDK provides specific exception classes to handle errors gracefully. Use these to catch and respond to issues like invalid API keys, unsupported languages, or incorrect speaker descriptions.

```python
from djelia.utils.exceptions import AuthenticationError, APIError, ValidationError, LanguageError, SpeakerError

try:
    response = djelia_client.translation.translate(request=request, version=Versions.v1)
    print(f"Translation: {response.text}")
except AuthenticationError as e:
    print(f"Authentication error (check API key): {e}")
except LanguageError as e:
    print(f"Invalid or unsupported language: {e}")
except ValidationError as e:
    print(f"Validation error (e.g., invalid input): {e}")
except APIError as e:
    print(f"API error (status {e.status_code}): {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## <h3 style="color:#00FFFF;"> Common Exceptions:

- **AuthenticationError**: Invalid or expired API key (HTTP 401).
- **APIError**: General API issues, including forbidden access (403) or resource not found (404).
- **ValidationError**: Invalid inputs, such as missing audio files or incorrect parameters (422).
- **LanguageError**: Unsupported source or target language.
- **SpeakerError**: Invalid speaker ID (TTS v1) or description missing a supported speaker (TTS v2).

Check logs for detailed errors, and ensure your `.env` file includes a valid `DJELIA_API_KEY` and `TEST_AUDIO_FILE`.

## <h3 style="color:#00FFFF;"> Explore the Djelia SDK Cookbook

Want to take your Djelia SDK skills to the next level? Check out the **Djelia SDK Cookbook** for a comprehensive example that puts it all together! The cookbook demonstrates:

- **Full Test Suite**: Run synchronous and asynchronous tests for translation, transcription, and TTS, with detailed summaries.
- **Error Handling**: Robust try-except blocks and logging to catch and debug issues.
- **Configuration Management**: Load API keys and audio paths from a `.env` file with validation.
- **Advanced Features**: Parallel API operations, version management, and streaming capabilities.
- **Modular Design**: Organized code structure for easy customization.

To run the cookbook, clone the repository, install dependencies, and execute:

```bash
git clone https://github.com/djelia/djelia-python-sdk.git
pip install git+https://github.com/djelia/djelia-python-sdk.git python-dotenv

cd djelia-python-sdk
python -m cookbook.main
```

Make sure your `.env` file includes `DJELIA_API_KEY` and `TEST_AUDIO_FILE`. The cookbook is perfect for developers who want a ready-to-use template for building real-world applications with the Djelia SDK.

## <h3 style="color:#00FFFF;"> Wrapping Up

And there you have it a full workshop on using the Djelia Python SDK! You've installed it, set up clients, and mastered translation, transcription, and text-to-speech both synchronously and asynchronously. Pretty cool, right? Feel free to tweak the code, explore different languages and voices, and check out the Djelia SDK Cookbook for a deeper dive.

**Pro tip**: The async methods are perfect for applications that need to handle multiple operations simultaneously. The streaming features are fantastic for realtime applications. And remember, Bambara is just one of the beautiful African languages you can work with!

<span style="color:red"><strong>IMPORTANT</strong></span>: If you encounter any issues, please create an issue in the repository, explain the problem you encountered (include logs if possible), and tag @sudoping01.

**Great job, bro 🫂! This is a fantastic integration guide built with ❤️ for 🇲🇱 and beyond!**<br>