"""Command-line interface for the Djelia Python SDK.

Exposes translation, transcription and text-to-speech through a ``djelia``
console command built with Typer and Rich.

Run ``djelia --help`` for the available commands.
"""

from __future__ import annotations

import sys

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ModuleNotFoundError as exc:  # pragma: no cover - guidance only
    missing = exc.name
    sys.stderr.write(
        f"The Djelia CLI needs '{missing}'. Install the CLI extra with:\n"
        '    pip install "djelia[cli]"\n'
    )
    raise SystemExit(1)

from djelia import Djelia
from djelia.models import Language, Versions

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Djelia SDK — translation, transcription and text-to-speech for "
    "African languages.",
)


# ------------------------------------------------------------------
# Shared state and helpers
# ------------------------------------------------------------------
class State:
    api_key: str | None = None
    base_url: str | None = None


state = State()

LANG_ALIASES = {
    "en": Language.ENGLISH,
    "eng": Language.ENGLISH,
    "english": Language.ENGLISH,
    "fr": Language.FRENCH,
    "fra": Language.FRENCH,
    "french": Language.FRENCH,
    "bm": Language.BAMBARA,
    "bam": Language.BAMBARA,
    "bambara": Language.BAMBARA,
}


def resolve_language(value: str) -> Language:
    """Accept friendly names (english/fr/bambara) or raw codes (eng_Latn)."""
    key = value.strip().lower()
    if key in LANG_ALIASES:
        return LANG_ALIASES[key]
    for lang in Language:
        if lang.value.lower() == key:
            return lang
    choices = "english, french, bambara"
    raise typer.BadParameter(f"unknown language {value!r} (try: {choices})")


def resolve_version(value: str) -> Versions:
    try:
        return Versions.from_value(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc))


def get_client() -> Djelia:
    """Build a sync client, surfacing auth/config errors cleanly."""
    try:
        return Djelia(api_key=state.api_key, base_url=state.base_url)
    except Exception as exc:  # noqa: BLE001 - present setup errors nicely
        err_console.print(f"[red]Could not initialize the Djelia client:[/] {exc}")
        err_console.print(
            "[dim]Set DJELIA_API_KEY or pass --api-key with a valid key.[/]"
        )
        raise typer.Exit(1)


def fail(message: str) -> None:
    err_console.print(f"[red]Error:[/] {message}")
    raise typer.Exit(1)


def read_text_arg(text: str) -> str:
    """Allow '-' to read the payload from stdin."""
    if text == "-":
        return sys.stdin.read().strip()
    return text


# ------------------------------------------------------------------
# Root callback (global options)
# ------------------------------------------------------------------
@app.callback()
def main(
    api_key: str | None = typer.Option(
        None,
        "--api-key",
        envvar="DJELIA_API_KEY",
        help="Djelia API key (defaults to the DJELIA_API_KEY env var).",
        show_default=False,
    ),
    base_url: str | None = typer.Option(
        None,
        "--base-url",
        envvar="BASE_URL",
        help="Override the API base URL.",
        show_default=False,
    ),
) -> None:
    state.api_key = api_key
    state.base_url = base_url


# ------------------------------------------------------------------
# languages
# ------------------------------------------------------------------
@app.command()
def languages() -> None:
    """List the languages supported for translation."""
    client = get_client()
    try:
        langs = client.translations.list_languages()
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))

    table = Table(title="Supported languages", header_style="bold", border_style="dim")
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    for lang in langs:
        table.add_row(lang.code, lang.name)
    console.print(table)
    console.print(f"[dim]{len(langs)} languages[/]")


# ------------------------------------------------------------------
# translate
# ------------------------------------------------------------------
@app.command()
def translate(
    text: str = typer.Argument(..., help="Text to translate ('-' reads stdin)."),
    source: str = typer.Option(
        ..., "--from", "-f", help="Source language (english/french/bambara or code)."
    ),
    target: str = typer.Option(
        ..., "--to", "-t", help="Target language (english/french/bambara or code)."
    ),
    model: str = typer.Option("v1", "--model", "-m", help="Model version (v1/v2)."),
    raw: bool = typer.Option(
        False, "--raw", help="Print only the translated text (script-friendly)."
    ),
) -> None:
    """Translate text between supported languages."""
    src = resolve_language(source)
    tgt = resolve_language(target)
    version = resolve_version(model)
    payload = read_text_arg(text)
    if not payload:
        fail("no text to translate")

    client = get_client()
    try:
        response = client.translations.create(
            text=payload, source=src, target=tgt, model=version
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))

    if raw:
        console.print(response.text, markup=False, highlight=False)
        return

    body = Text()
    body.append(payload, style="dim")
    body.append("\n\n→ ", style="green")
    body.append(response.text, style="bold")
    console.print(
        Panel(
            body,
            title=f"{src.value} → {tgt.value}",
            subtitle=f"model {version}",
            border_style="cyan",
        )
    )


# ------------------------------------------------------------------
# transcribe
# ------------------------------------------------------------------
@app.command()
def transcribe(
    file: str = typer.Argument(..., help="Path to the audio file."),
    model: str = typer.Option("v2", "--model", "-m", help="Model version (v1/v2)."),
    french: bool = typer.Option(
        False, "--french", help="Translate the transcription to French (v2)."
    ),
    stream: bool = typer.Option(
        False, "--stream", help="Stream segments as they are produced."
    ),
) -> None:
    """Transcribe an audio file to text."""
    import os

    if not os.path.exists(file):
        fail(f"audio file not found: {file}")
    version = resolve_version(model)
    client = get_client()

    try:
        if stream:
            _transcribe_stream(client, file, version, french)
            return

        result = client.audio.transcriptions.create(
            file=file, model=version, translate_to_french=french
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))

    if french or hasattr(result, "text"):
        console.print(
            Panel(result.text, title="Transcription (French)", border_style="blue")
        )
        return

    table = Table(title="Transcription", header_style="bold", border_style="dim")
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Start", justify="right")
    table.add_column("End", justify="right")
    table.add_column("Text")
    for i, seg in enumerate(result, 1):
        table.add_row(str(i), f"{seg.start:.2f}s", f"{seg.end:.2f}s", seg.text)
    console.print(table)
    console.print(f"[dim]{len(result)} segments[/]")


def _transcribe_stream(
    client: Djelia, file: str, version: Versions, french: bool
) -> None:
    count = 0
    with console.status("[cyan]transcribing…[/]", spinner="dots"):
        segments = client.audio.transcriptions.create(
            file=file, model=version, translate_to_french=french, stream=True
        )
        for seg in segments:
            count += 1
            if hasattr(seg, "start"):
                console.print(f"[cyan]{seg.start:6.2f}-{seg.end:6.2f}s[/]  {seg.text}")
            else:
                console.print(seg.text)
    console.print(f"[dim]{count} segments streamed[/]")


# ------------------------------------------------------------------
# speak (text-to-speech)
# ------------------------------------------------------------------
@app.command()
def speak(
    text: str = typer.Argument(..., help="Text to synthesize ('-' reads stdin)."),
    output: str = typer.Option(
        "output.wav", "--output", "-o", help="Where to write the audio file."
    ),
    model: str = typer.Option("v1", "--model", "-m", help="Model version (v1/v2)."),
    voice: int | None = typer.Option(None, "--voice", help="Speaker id for v1 (0-4)."),
    speaker: str | None = typer.Option(
        None,
        "--speaker",
        help="Speaker name for v2 (Moussa/Sekou/Seydou); builds a description.",
    ),
    description: str | None = typer.Option(
        None,
        "--description",
        help="Full v2 voice description (must name a supported speaker).",
    ),
    stream: bool = typer.Option(
        False, "--stream", help="Stream audio chunks (v2 only)."
    ),
    chunk_size: float = typer.Option(
        1.0, "--chunk-size", help="v2 chunk size (0.1-2.0)."
    ),
) -> None:
    """Synthesize speech from text and save it to a file."""
    version = resolve_version(model)
    payload = read_text_arg(text)
    if not payload:
        fail("no text to synthesize")

    if version == Versions.v2 and description is None:
        name = speaker or "Moussa"
        description = f"{name} speaks with a natural, clear tone"

    client = get_client()
    try:
        if stream:
            _speak_stream(client, payload, output, version, description, chunk_size)
        else:
            with console.status("[green]synthesizing…[/]", spinner="dots"):
                path = client.audio.speech.create(
                    input=payload,
                    voice=voice,
                    description=description,
                    model=version,
                    chunk_size=chunk_size,
                    output_file=output,
                )
            _report_audio(path)
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))


def _speak_stream(
    client: Djelia,
    text: str,
    output: str,
    version: Versions,
    description: str | None,
    chunk_size: float,
) -> None:
    import os

    chunks = 0
    total = 0
    with console.status("[green]streaming audio…[/]", spinner="dots") as status:
        for chunk in client.audio.speech.create(
            input=text,
            description=description,
            model=version,
            chunk_size=chunk_size,
            stream=True,
            output_file=output,
        ):
            chunks += 1
            total += len(chunk)
            status.update(
                f"[green]streaming audio…[/] {chunks} chunks · {total:,} bytes"
            )
    console.print(f"[dim]{chunks} chunks · {total:,} bytes[/]")
    if os.path.exists(output):
        _report_audio(output)


def _report_audio(path) -> None:
    import os

    if isinstance(path, (bytes, bytearray)):
        console.print(f"[green]✓[/] received {len(path):,} bytes")
        return
    try:
        size = os.path.getsize(path)
        console.print(f"[green]✓[/] saved [bold]{path}[/] ({size:,} bytes)")
    except OSError:
        console.print(f"[green]✓[/] saved [bold]{path}[/]")


# ------------------------------------------------------------------
# version
# ------------------------------------------------------------------
@app.command()
def version() -> None:
    """Show SDK and API version information."""
    try:
        from importlib.metadata import version as pkg_version

        sdk_version = pkg_version("djelia")
    except Exception:  # noqa: BLE001
        sdk_version = "unknown"

    table = Table(show_header=False, border_style="dim")
    table.add_column(style="cyan")
    table.add_column()
    table.add_row("SDK version", sdk_version)
    table.add_row("Latest API model", str(Versions.latest()))
    table.add_row(
        "Available models", ", ".join(str(v) for v in Versions.all_versions())
    )
    console.print(table)


if __name__ == "__main__":
    app()
