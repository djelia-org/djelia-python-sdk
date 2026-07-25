from __future__ import annotations

import enum
import os
import sys
from typing import List, Optional, Tuple

import typer
from rich.prompt import Confirm, Prompt
from rich.table import Table

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .config import Config
from .cookbook import GROUP_ORDER, GROUPS, DjeliaTestSuite
from .utils import Reporter, banner, console, render_summary

app = typer.Typer(
    add_completion=False,
    help="Interactive test suite for the Djelia Python SDK (OpenAI-style API).",
)


class Mode(str, enum.Enum):
    sync = "sync"
    async_ = "async"
    both = "both"


def _groups_table() -> Table:
    table = Table(
        title="Available test groups", header_style="bold", border_style="dim"
    )
    table.add_column("#", justify="right", style="cyan")
    table.add_column("Group")
    table.add_column("Label")
    table.add_column("Sync", justify="center")
    table.add_column("Async", justify="center")
    for i, key in enumerate(GROUP_ORDER, 1):
        spec = GROUPS[key]
        table.add_row(
            str(i),
            key,
            str(spec["label"]),
            "✓" if spec["sync"] else "—",
            "✓" if spec["async"] else "—",
        )
    return table


def _select_interactively() -> Tuple[List[str], str]:
    console.print(_groups_table())
    console.print(
        "[dim]Enter group numbers separated by commas (e.g. 1,3,4), "
        "or press Enter for all.[/dim]"
    )
    raw = Prompt.ask("Groups", default="all")

    if raw.strip().lower() in ("", "all"):
        groups = list(GROUP_ORDER)
    else:
        groups = []
        for token in raw.split(","):
            token = token.strip()
            if token.isdigit() and 1 <= int(token) <= len(GROUP_ORDER):
                groups.append(GROUP_ORDER[int(token) - 1])
            elif token in GROUPS:
                groups.append(token)
            else:
                console.print(f"[yellow]Ignoring unknown group: {token}[/]")

    mode = Prompt.ask("Mode", choices=["sync", "async", "both"], default="both")
    return groups, mode


@app.command()
def run(
    group: List[str] = typer.Option(
        [],
        "--group",
        "-g",
        help=f"Test group to run (repeatable). One of: {', '.join(GROUP_ORDER)}.",
    ),
    mode: Mode = typer.Option(
        Mode.both, "--mode", "-m", help="Run sync tests, async tests, or both."
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Pick groups and mode from a menu."
    ),
    list_groups: bool = typer.Option(
        False, "--list", "-l", help="List available test groups and exit."
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        envvar="DJELIA_API_KEY",
        help="Djelia API key.",
        show_default=False,
    ),
    audio: Optional[str] = typer.Option(
        None, "--audio", "-a", help="Path to the audio file used for transcription."
    ),
    output_dir: str = typer.Option(
        "cookbook_output",
        "--output-dir",
        "-o",
        help="Where generated audio is written.",
    ),
    keep_audio: bool = typer.Option(
        False, "--keep-audio", help="Keep generated audio instead of cleaning it up."
    ),
    max_segments: int = typer.Option(
        3, "--max-segments", help="Streaming transcription segments to display."
    ),
    max_chunks: int = typer.Option(
        5, "--max-chunks", help="Streaming TTS chunks to display."
    ),
):
    """Run the Djelia SDK test suite."""
    if list_groups:
        console.print(_groups_table())
        raise typer.Exit()

    banner()

    config = Config.load()
    if api_key:
        config.api_key = api_key
    if audio:
        config.audio_file_path = audio
    config.output_dir = output_dir
    config.keep_audio = keep_audio
    config.max_stream_segments = max_segments
    config.max_stream_chunks = max_chunks

    mode_value = "async" if mode == Mode.async_ else mode.value

    if interactive:
        groups, mode_value = _select_interactively()
    elif group:
        groups = []
        for g in group:
            if g not in GROUPS:
                console.print(f"[red]Unknown group:[/] {g}")
                raise typer.Exit(1)
            groups.append(g)
    else:
        groups = list(GROUP_ORDER)

    reporter = Reporter(console)
    if not config.api_key:
        console.print("[red]DJELIA_API_KEY is not set[/] (use --api-key or a .env file).")
        raise typer.Exit(1)

    try:
        suite = DjeliaTestSuite(config, reporter)
    except Exception as exc:  # noqa: BLE001 - surface setup errors cleanly
        console.print(f"[red]Failed to initialize the client:[/] {exc}")
        raise typer.Exit(1)

    if not suite.validate():
        console.print("[red]Setup validation failed. Fix the issues above.[/]")
        raise typer.Exit(1)

    if not groups:
        console.print("[yellow]No groups selected. Nothing to do.[/]")
        raise typer.Exit()

    try:
        suite.run(groups, mode_value)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/]")

    render_summary(reporter)

    if any(r.status == "fail" for r in reporter.results):
        if Confirm.ask("\n[dim]Show tracebacks for failures?[/]", default=False):
            for r in reporter.results:
                if r.status == "fail" and r.error:
                    console.print(f"\n[red bold]{r.name}[/]")
                    console.print(r.error)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
