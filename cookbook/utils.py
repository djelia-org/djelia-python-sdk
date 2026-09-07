from __future__ import annotations

import time
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()

STATUS_STYLE = {"pass": "green", "fail": "red", "skip": "yellow"}
STATUS_ICON = {"pass": "✓", "fail": "✗", "skip": "–"}

# Colour per operation kind, echoed in the live line and the metrics table.
KIND_STYLE = {
    "languages": "magenta",
    "translate": "cyan",
    "transcribe": "blue",
    "stream": "yellow",
    "tts": "green",
    "gather": "white",
}


# ================================================
#                  Data model
# ================================================


@dataclass
class OpEvent:
    """A single timed SDK call within a test case."""

    kind: str
    label: str
    seconds: float
    detail: str = ""
    ok: bool = True


@dataclass
class TestResult:
    name: str
    group: str
    status: str  # "pass" | "fail" | "skip"
    detail: str = ""
    seconds: float = 0.0
    events: list[OpEvent] = field(default_factory=list)
    error: str | None = None  # traceback, when status == "fail"


class _OpHandle:
    """Mutable handle a test body fills in while an operation is running."""

    def __init__(self, kind: str, label: str) -> None:
        self.kind = kind
        self.label = label
        self.detail = ""
        self.ok = True

    def set(self, detail: str) -> None:
        self.detail = detail


class Case:
    """One test case: owns its timed operations and reports live as they finish."""

    def __init__(self, name: str, group: str, console: Console) -> None:
        self.name = name
        self.group = group
        self.console = console
        self.events: list[OpEvent] = []
        self.status = "pass"
        self.detail = ""
        self.seconds = 0.0
        self.error: str | None = None

    @contextmanager
    def op(self, kind: str, label: str) -> Iterator[_OpHandle]:
        """Time an SDK call and print a live line the moment it completes."""
        handle = _OpHandle(kind, label)
        t0 = time.perf_counter()
        try:
            yield handle
        except Exception:
            handle.ok = False
            raise
        finally:
            seconds = time.perf_counter() - t0
            self.events.append(
                OpEvent(kind, handle.label, seconds, handle.detail, handle.ok)
            )
            self._live(kind, handle, seconds)

    def _live(self, kind: str, handle: _OpHandle, seconds: float) -> None:
        style = KIND_STYLE.get(kind, "white")
        icon = "[green]✓[/]" if handle.ok else "[red]✗[/]"
        detail = f" {handle.detail}" if handle.detail else ""
        self.console.print(
            f"  {icon} [{style}]{kind:<10}[/] {handle.label:<22} "
            f"[dim]{seconds:6.2f}s[/]{detail}"
        )

    def note(self, message: str) -> None:
        """A live, untimed progress line (e.g. a streamed segment)."""
        self.console.print(f"    [dim]· {message}[/]")

    def done(self, detail: str) -> None:
        self.detail = detail


class Reporter:
    """Runs test cases, streams live metrics, and collects results."""

    def __init__(self, console: Console = console) -> None:
        self.console = console
        self.results: list[TestResult] = []

    def section(self, title: str, style: str = "cyan") -> None:
        self.console.print()
        self.console.print(Rule(f"[bold {style}]{title}[/]", style=style))

    def ok(self, message: str) -> None:
        self.console.print(f"  [green]✓[/] {message}")

    def info(self, message: str) -> None:
        self.console.print(f"  [dim]…[/] [dim]{message}[/]")

    def fail(self, message: str) -> None:
        self.console.print(f"  [red]✗[/] {message}")

    def record(self, result: TestResult) -> None:
        self.results.append(result)

    @contextmanager
    def case(self, name: str, group: str) -> Iterator[Case]:
        """Time a test, catch failures, render its metrics table in real time."""
        self.section(name)
        case = Case(name, group, self.console)
        t0 = time.perf_counter()
        try:
            yield case
        except Exception as exc:  # noqa: BLE001 - report every failure
            case.status = "fail"
            case.detail = str(exc)
            case.error = traceback.format_exc()
            self.fail(f"{name}: {exc}")
        case.seconds = time.perf_counter() - t0
        self._render_case_metrics(case)
        self.record(
            TestResult(
                name=case.name,
                group=case.group,
                status=case.status,
                detail=case.detail,
                seconds=case.seconds,
                events=case.events,
                error=case.error,
            )
        )

    def _render_case_metrics(self, case: Case) -> None:
        if not case.events:
            return
        table = Table(
            box=ROUNDED,
            border_style="dim",
            header_style="bold",
            title=f"[dim]{case.name} — operations[/dim]",
            title_justify="left",
            expand=True,
        )
        table.add_column("Operation")
        table.add_column("Kind")
        table.add_column("Result")
        table.add_column("Time", justify="right")
        for ev in case.events:
            style = KIND_STYLE.get(ev.kind, "white")
            marker = "" if ev.ok else "[red]✗ [/]"
            table.add_row(
                f"{marker}{ev.label}",
                f"[{style}]{ev.kind}[/]",
                ev.detail or "—",
                f"{ev.seconds:.2f}s",
            )
        self.console.print(table)

        measured = sum(e.seconds for e in case.events)
        slowest = max(case.events, key=lambda e: e.seconds)
        self.console.print(
            f"  [dim]measured {measured:.2f}s of {case.seconds:.2f}s · "
            f"slowest: {slowest.label} ({slowest.seconds:.2f}s)[/dim]"
        )


# ================================================
#                  Rendering helpers
# ================================================


def banner() -> None:
    console.print(
        Panel(
            Text("Djelia SDK Test Suite", justify="center", style="bold yellow"),
            subtitle="[dim]OpenAI-style API · translation · transcription · TTS[/dim]",
            border_style="cyan",
            box=ROUNDED,
        )
    )


def render_summary(reporter: Reporter) -> None:
    results = reporter.results
    if not results:
        console.print("[dim]No tests were run.[/dim]")
        return

    table = Table(
        title="[bold]Test Summary[/bold]",
        header_style="bold",
        border_style="dim",
        box=ROUNDED,
        expand=True,
    )
    table.add_column("Test")
    table.add_column("Group", style="dim")
    table.add_column("Ops", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")
    table.add_column("Details")

    for r in results:
        style = STATUS_STYLE.get(r.status, "white")
        icon = STATUS_ICON.get(r.status, "?")
        table.add_row(
            r.name,
            r.group,
            str(len(r.events)) if r.events else "—",
            f"[{style}]{icon} {r.status}[/]",
            f"{r.seconds:.2f}s",
            r.detail or "—",
        )

    console.print()
    console.print(table)

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    skipped = sum(1 for r in results if r.status == "skip")
    total_time = sum(r.seconds for r in results)
    total_ops = sum(len(r.events) for r in results)

    summary = (
        f"[green]{passed} passed[/]"
        + (f" · [red]{failed} failed[/]" if failed else "")
        + (f" · [yellow]{skipped} skipped[/]" if skipped else "")
        + f"  [dim]· {total_ops} API calls in {total_time:.2f}s[/dim]"
    )
    console.print(
        Panel(
            summary,
            border_style="green" if not failed else "red",
            box=ROUNDED,
        )
    )
