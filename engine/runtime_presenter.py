"""Render structured runtime events to CLI or TUI output."""
from __future__ import annotations

from typing import Iterable


def _emit_text(text: str) -> None:
    try:
        from tui import get_app, is_tui_mode

        app = get_app()
        if app is not None and is_tui_mode():
            app.add_output(text)
            return
    except ImportError:
        pass

    print(text)


def render_runtime_event(event) -> None:
    """Render a runtime event using the active output backend."""
    kind = getattr(event, "kind", "text")
    if kind == "lines":
        for line in getattr(event, "lines", ()):
            _emit_text(str(line))
        return

    text = getattr(event, "text", "")
    if text:
        _emit_text(str(text))
