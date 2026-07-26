<h1 align="center">
    Djelia Python SDK
</h1>
<p align="center">
    <em>Advanced AI for African Languages - Translation, Transcription & Text-to-Speech</em>
</p>

<!-- prettier-ignore -->
<p align="center">
    <a href="https://pypi.org/project/djelia/"><img src="https://img.shields.io/pypi/v/djelia.svg?label=pypi%20(stable)" alt="PyPI version"></a>
</p>

The Djelia Python library provides convenient access to the Djelia REST API for African languages (with first-class support for Bambara / Bamanankan) from any Python application. The library includes type definitions for request params and response fields, and offers both synchronous and asynchronous clients powered by the same underlying implementation.

## Documentation

The REST API documentation can be found at [djelia.cloud/docs](https://djelia.cloud/docs). API keys are created and managed at the [Djelia Console](https://console.djelia.cloud).

## Installation

```sh
# install from PyPI
pip install djelia
```

Install directly from GitHub:

```sh
pip install git+https://github.com/djelia-org/djelia-python-sdk.git
```

Or use [uv](https://github.com/astral-sh/uv) for faster resolution:

```sh
uv pip install djelia
```

Optional extras:

| Extra | Installs | Use for |
|-------|----------|---------|
| `djelia[cli]` | `typer`, `rich` | The `djelia` command-line interface |
| `djelia[cookbook]` | `typer`, `rich`, `python-dotenv` | The interactive test-suite cookbook |

```sh
pip install "djelia[cli]"
```

## Usage

The primary interface is a resource-based client. Set your API key in the environment:

```sh
export DJELIA_API_KEY="your-api-key"
```

```python
from djelia import Djelia
from djelia.models import Language, Versions

client = Djelia()
# or pass it explicitly:
# client = Djelia(api_key="your-api-key")


response = client.translations.create(
    text="Hello, how are you today?",
    source=Language.ENGLISH,
    target=Language.BAMBARA,
    model=Versions.v1,
)

print(response.text)
```



## Async usage

Simply import `DjeliaAsync` instead of `Djelia` and use `await` with each API call:

```python
import asyncio
from djelia import DjeliaAsync
from djelia.models import Language, Versions

async def main() -> None:
    async with DjeliaAsync() as client:
        response = await client.translations.create(
            text="Hello, how are you today?",
            source=Language.ENGLISH,
            target=Language.BAMBARA,
            model=Versions.v1,
        )
        print(response.text)

asyncio.run(main())
```

Non-streaming calls use the same methods with `await`. Streaming responses additionally require `async for`, as shown below.

## Streaming responses

Transcription and text-to-speech support streaming so you can process results as they're produced, rather than waiting for the full response.

```python
from djelia import Djelia
from djelia.models import Versions

client = Djelia()

for segment in client.audio.transcriptions.create(
    file="/path/to/your/audio/file.wav", 
    stream=True,
    model=Versions.v2,
):
    print(f"[{segment.start:.2f}s]: {segment.text}")
```

The async client uses the exact same interface:

```python
async def stream_transcribe():
    async with DjeliaAsync() as c:
        stream = await c.audio.transcriptions.create(
            file="/path/to/your/audio/file.wav", 
            stream=True,
            model=Versions.v2,
        )
        async for segment in stream:
            print(f"[{segment.start:.2f}s]: {segment.text}")
```

Text-to-speech streaming (**v2 only**) works the same way, yielding raw audio chunks as they're generated:

```python
for chunk in client.audio.speech.create(
    input="An filɛ ni ye yɔrɔ minna ni an ye an sigi ...",
    description="Seydou speaks clearly and naturally",
    chunk_size=1.0,
    output_file="streamed_audio.wav",
    stream=True,
    model=Versions.v2,
):
    print(f"Chunk: {len(chunk)} bytes")
```

## Resources

| Capability | Resource | Description |
|------------|----------|--------------|
| Translation | `client.translations` | Translate between French, English, and Bambara |
| Transcription | `client.audio.transcriptions` | Speech-to-text with timestamps, optional French translation, and streaming |
| Text-to-Speech | `client.audio.speech` | Natural speech synthesis with numbered voices (v1) or described voices (v2), plus streaming |

### Translation

```python
from djelia.models import Language, Versions, TranslationResponse

# List supported languages
for lang in client.translations.list_languages():
    print(f"{lang.name}: {lang.code}")

# Translate text
response: TranslationResponse = client.translations.create(
    text="Hello, how are you today?",
    source=Language.ENGLISH,
    target=Language.BAMBARA,
    model=Versions.v1,
)
print(response.text)
```

### Transcription

```python
from djelia.models import Versions

transcription = client.audio.transcriptions.create(
    file="/path/to/your/audio/file.wav",
    model=Versions.v2,
)
for segment in transcription:
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")

# Transcribe and translate to French in one call (v2 only)
french = client.audio.transcriptions.create(
    file="/path/to/your/audio/file.wav", 
    translate_to_french=True,
    model=Versions.v2,
)
print(french.text)
```

### Text-to-Speech

Choose numbered speakers (v1) or describe exactly how the voice should sound (v2).

```python
# v1 - speaker ID (0-4)
path = client.audio.speech.create(
    input="Aw ni ce, i ka kɛnɛ wa?",
    voice=1,
    output_file="hello_v1.wav",
    model=Versions.v1,
)
print(f"Audio saved to: {path}")

# v2 - natural description; must name a supported speaker: Moussa, Sekou, or Seydou
path = client.audio.speech.create(
    input="Aw ni ce, i ka kɛnɛ wa?",
    description="Seydou speaks with a warm, welcoming tone",
    chunk_size=1.0,          # controls pacing (0.1 - 2.0)
    output_file="hello_v2.wav",
    model=Versions.v2,
)
print(f"Natural audio saved to: {path}")
```

> [!WARNING]
> The `description` must include one of the supported speakers. `"Moussa speaks with a warm tone"` is valid; `"Natural tone"` raises a `SpeakerError`.

## Version management

The SDK supports multiple API versions through the `Versions` enum.

```python
from djelia.models import Versions

Versions.latest()                              # v2
[str(v) for v in Versions.all_versions()]      # ['v1', 'v2']
Versions.from_value("v2")                      # accepts enum, int, or "v2"-style strings
```

| Version | Translation | Transcription | Text-to-Speech |
|---------|-------------|----------------|------------------|
| **v1** | ✅ | ✅ | Numbered voices (`voice=0..4`) |
| **v2** | ✅ | ✅ (+ French, streaming) | Described voices + streaming |

## Async & parallel operations

Run multiple operations concurrently with `asyncio.gather` and the async client - ideal for high-throughput applications.

```python
import asyncio
from djelia import DjeliaAsync
from djelia.models import Language, Versions

async def parallel_operations():
    async with DjeliaAsync() as client:
        results = await asyncio.gather(
            client.translations.create(
                text="Hello", source=Language.ENGLISH,
                target=Language.BAMBARA, model=Versions.v1,
            ),
            client.audio.transcriptions.create(file="audio.wav", model=Versions.v2),
            client.audio.speech.create(
                input="Aw ni ce, i ka kɛnɛ wa?",
                description="Moussa speaks with a clear tone",
                chunk_size=1.0,
                output_file="parallel_tts.wav",
                model=Versions.v2,
            ),
            return_exceptions=True,
        )
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"Operation {i} failed: {result}")
            else:
                print(f"Operation {i} succeeded: {type(result).__name__}")

asyncio.run(parallel_operations())
```

## Handling errors

The SDK raises specific exception classes so you can respond precisely.

```python
from djelia.utils.exceptions import (
    AuthenticationError, APIError, ValidationError, LanguageError, SpeakerError,
)

try:
    response = client.translations.create(
        text="Hello, how are you today?",
        source=Language.ENGLISH,
        target=Language.BAMBARA,
        model=Versions.v1,
    )
    print(response.text)
except AuthenticationError as e:
    print(f"Authentication error (check API key): {e}")
except LanguageError as e:
    print(f"Invalid or unsupported language: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except APIError as e:
    print(f"API error (status {e.status_code}): {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

| Exception | Meaning |
|-----------|---------|
| `AuthenticationError` | Invalid or expired API key (HTTP 401) |
| `APIError` | General API issues - forbidden (403), not found (404), etc. |
| `ValidationError` | Invalid inputs, e.g. missing audio file or bad parameters (422) |
| `LanguageError` | Unsupported source or target language |
| `SpeakerError` | Invalid speaker ID (v1) or description missing a supported speaker (v2) |

## Command line interface

Install the CLI extra and the `djelia` command becomes available in your terminal:

```sh
pip install "djelia[cli]"
export DJELIA_API_KEY="your-api-key"   # or pass --api-key on any command
```

| Command | Description |
|---------|--------------|
| `djelia languages` | List the languages supported for translation |
| `djelia translate` | Translate text between supported languages |
| `djelia transcribe` | Transcribe an audio file to text |
| `djelia speak` | Synthesize speech from text and save it to a file |
| `djelia version` | Show SDK and available API model versions |

Global options `--api-key` (env `DJELIA_API_KEY`) and `--base-url` (env `BASE_URL`) work on every command. Run `djelia --help` or `djelia <command> --help` for details.

```sh
# Full panel output
djelia translate "Hello, how are you?" --from english --to bambara

# Script-friendly: print only the translated text
djelia translate "Good morning" -f en -t fr --raw

# Read text from stdin
echo "Hello" | djelia translate - --from english --to bambara

# Segments with timestamps
djelia transcribe audio.wav --model v2

# Stream segments as they are produced
djelia transcribe audio.wav --model v2 --stream

# v2 with a named speaker (Moussa / Sekou / Seydou)
djelia speak "Aw ni ce, i ka kɛnɛ wa?" --model v2 --speaker Sekou -o hello_v2.wav
```

## Cookbook

The **Djelia SDK Cookbook** is an interactive, test suite that exercises the whole API with live metrics - timed calls, a per-test operations table, and a pass/fail summary.

```sh
git clone https://github.com/djelia-org/djelia-python-sdk.git
cd djelia-python-sdk
pip install -e ".[cookbook]"   # SDK plus typer, rich, python-dotenv

python -m cookbook                              # run everything (sync + async)
python -m cookbook --list                       # list available test groups
python -m cookbook -g translation -g tts --mode sync   # a couple of groups, sync only
python -m cookbook --interactive                # pick groups and mode from a menu
```

Generated audio is written to `cookbook_output/` and cleaned up automatically (pass `--keep-audio` to keep it). Make sure your `.env` includes `DJELIA_API_KEY` (and optionally `TEST_AUDIO_FILE`).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

We are keen for your feedback - please open an [issue](https://github.com/djelia-org/djelia-python-sdk/issues) with questions, bugs, or suggestions, and tag [@sudoping01](https://github.com/sudoping01).

---

<p align="center">
    Built with ❤️ for 🇲🇱 and beyond.
</p>