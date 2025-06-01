import logging

from djelia.models import FrenchTranscriptionResponse, TranscriptionSegment

# ================================================
#                  Console Utilities
# ================================================


class ConsoleColor:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    PURPLE = "\033[35m"
    BLUE = "\033[34m"
    GRAY = "\033[37m"
    RESET = "\033[0m"


# ================================================
#                  Utility Functions
# ================================================


def print_success(message: str) -> None:
    print(f"{ConsoleColor.GREEN}✓ {message}{ConsoleColor.RESET}")


def print_error(message: str) -> None:
    print(f"{ConsoleColor.RED}✗ {message}{ConsoleColor.RESET}")
    logging.error(message)


def print_info(message: str) -> None:
    print(f"{ConsoleColor.GRAY}ℹ {message}{ConsoleColor.RESET}")


def print_summary(test_results: dict) -> None:
    print(f"\n{ConsoleColor.CYAN}{'=' * 60}{ConsoleColor.RESET}")
    print(f"{'Test Summary':^60}")
    print(f"{ConsoleColor.CYAN}{'=' * 60}{ConsoleColor.RESET}")
    print(f"{'Test':<40} {'Status':<10} {'Details'}")
    print(f"{ConsoleColor.GRAY}{'-' * 60}{ConsoleColor.RESET}")

    for test, (status, details) in sorted(test_results.items()):
        color = ConsoleColor.GREEN if status == "Success" else ConsoleColor.RED
        print(f"{test:<40} {color}{status:<10}{ConsoleColor.RESET} {details}")


def handle_transcription_result(
    transcription: list[TranscriptionSegment] | FrenchTranscriptionResponse,
    version_info: str,
) -> None:
    if isinstance(transcription, list) and transcription:
        print_success(f"Transcription {version_info}: {len(transcription)} segments")
        segment = transcription[0]
        print_success(
            f"Sample: {segment.start:.1f}s-{segment.end:.1f}s: "
            f"'{ConsoleColor.YELLOW}{segment.text}{ConsoleColor.RESET}'"
        )
    elif hasattr(transcription, "text"):
        print_success(
            f"Transcription {version_info}: "
            f"'{ConsoleColor.YELLOW}{transcription.text}{ConsoleColor.RESET}'"
        )
    else:
        print_error(f"Unexpected result format for {version_info}")


def process_result(name: str, result: object) -> None:
    if isinstance(result, Exception):
        print_error(f"{name}: {str(result)}")
    else:
        print_success(f"{name}: Received {type(result).__name__}")
