"""Cross-platform quiz timer with timeout and input capture.

Uses msvcrt.kbhit() on Windows and select.select() on Unix.
Abstracted behind a protocol class so callers don't need platform checks.
"""

from __future__ import annotations

import sys
import time
from typing import Protocol


class TimerBackend(Protocol):
    """Protocol for platform-specific timer backends."""

    def wait_for_keypress(self, timeout_seconds: int) -> tuple[str | None, float]:
        """Wait up to timeout_seconds for a single keypress.

        Returns (key_char, elapsed_seconds) or (None, elapsed) on timeout.
        """
        ...


class UnixTimerBackend:
    """Unix: uses select.select on stdin."""

    def wait_for_keypress(self, timeout_seconds: int) -> tuple[str | None, float]:
        import select
        import termios  # type: ignore[import-untyped]
        import tty  # type: ignore[import-untyped]

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)  # type: ignore[attr-defined]
        start = time.monotonic()

        try:
            tty.setraw(fd)  # type: ignore[attr-defined]
            ready, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
            elapsed = time.monotonic() - start

            if ready:
                char = sys.stdin.read(1)
                return char, elapsed
            return None, elapsed
        except (termios.error, OSError):  # type: ignore[attr-defined]
            elapsed = time.monotonic() - start
            return None, elapsed
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # type: ignore[attr-defined]
            except (termios.error, Exception):  # type: ignore[attr-defined]
                pass


class WindowsTimerBackend:
    """Windows: uses msvcrt.kbhit() with polling."""

    def wait_for_keypress(self, timeout_seconds: int) -> tuple[str | None, float]:
        import msvcrt  # type: ignore[import-untyped]

        start = time.monotonic()
        poll_interval = 0.05  # 50ms polling

        while True:
            elapsed = time.monotonic() - start
            if elapsed >= timeout_seconds:
                return None, elapsed

            if msvcrt.kbhit():  # type: ignore[attr-defined]
                char: str = msvcrt.getch()  # type: ignore[attr-defined]
                # On Windows, getch returns bytes; decode to str
                if isinstance(char, bytes):
                    try:
                        char = char.decode("utf-8", errors="replace")
                    except Exception:
                        char = "?"
                elapsed = time.monotonic() - start
                return char, elapsed

            remaining = timeout_seconds - elapsed
            time.sleep(min(poll_interval, remaining))


class FallbackTimerBackend:
    """Fallback: uses input() with a timeout thread (least reliable but always works)."""

    def wait_for_keypress(self, timeout_seconds: int) -> tuple[str | None, float]:
        import threading

        result: list[str | None] = [None]

        def reader() -> None:
            try:
                result[0] = sys.stdin.readline().strip()
            except Exception:
                pass

        start = time.monotonic()
        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)

        elapsed = time.monotonic() - start
        if result[0] is not None:
            return result[0][0] if result[0] else "", elapsed
        return None, elapsed


def get_timer_backend() -> TimerBackend:
    """Detect platform and return the appropriate timer backend."""
    if sys.platform == "win32":
        return WindowsTimerBackend()
    elif sys.platform in ("darwin", "linux", "linux2"):
        return UnixTimerBackend()
    return FallbackTimerBackend()


def timed_input(
    prompt: str,
    timeout_seconds: int = 60,
    valid_keys: set[str] | None = None,
    backend: TimerBackend | None = None,
) -> tuple[str | None, float]:
    """Display a prompt and wait for a single keypress with timeout.

    Args:
        prompt: Text to display before waiting.
        timeout_seconds: Maximum time to wait in seconds.
        valid_keys: Set of accepted keys (e.g. {'1','2','3','4','s','q'}).
                    Pressing an invalid key is ignored and the timer continues.
        backend: Timer backend (auto-detected if None).

    Returns:
        (key_char, elapsed_seconds) — key_char is None on timeout.
    """
    if backend is None:
        backend = get_timer_backend()

    if valid_keys is None:
        valid_keys = {"1", "2", "3", "4"}

    print(prompt, end="", flush=True)
    char, elapsed = backend.wait_for_keypress(timeout_seconds)

    if char is not None and char in valid_keys:
        print(char)  # echo valid key
        return char, elapsed
    elif char is not None:
        # Invalid key — echo and try again with remaining time
        remaining = max(0, int(timeout_seconds - elapsed))
        if remaining > 1:
            print(f"\n  Invalid key '{char}'. Valid: {sorted(valid_keys)}")
            return timed_input(prompt, remaining, valid_keys, backend)
        return None, elapsed
    else:
        print()  # newline on timeout
        return None, elapsed


def format_timer(seconds: int) -> str:
    """Format seconds as MM:SS."""
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"
