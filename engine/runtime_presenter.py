"""Render structured runtime events to CLI or TUI output."""
from __future__ import annotations

import sys


def _emit_text(text: str) -> None:
    try:
        from tui import get_app, is_tui_mode

        app = get_app()
        if app is not None and is_tui_mode():
            app.add_output(text)
            return
    except ImportError:
        pass

    sys.stdout.write(text)
    sys.stdout.flush()


def render_runtime_event(event) -> None:
    """Render a runtime event using the active output backend."""
    text = getattr(event, "text", "")
    if text:
        _emit_text(text)
        return

    lines = getattr(event, "lines", ())
    if lines:
        _emit_text("\n".join(str(line) for line in lines) + "\n")


def flush_runtime_events() -> None:
    """Render and clear all queued runtime events."""
    from engine.runtime_events import drain_runtime_events

    for event in drain_runtime_events():
        render_runtime_event(event)
