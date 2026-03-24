"""Structured runtime events emitted by execution code."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple


@dataclass(frozen=True)
class RuntimeEvent:
    """A structured runtime event that can be rendered by a presenter."""

    kind: str
    text: str = ""
    lines: Tuple[str, ...] = ()
    data: Dict[str, Any] = field(default_factory=dict)


_RUNTIME_EVENTS: List[RuntimeEvent] = []


def emit_runtime_event(event: RuntimeEvent) -> RuntimeEvent:
    """Record and render a runtime event."""
    _RUNTIME_EVENTS.append(event)
    from engine.runtime_presenter import render_runtime_event

    render_runtime_event(event)
    return event


def emit_text(*args: Any, sep: str = " ", end: str = "\n", kind: str = "text", data: Dict[str, Any] | None = None) -> RuntimeEvent:
    """Emit text like print, but through the runtime event layer."""
    if not args:
        return emit_blank_line()
    text = sep.join(str(arg) for arg in args)
    if end and end != "\n":
        text = f"{text}{end}"
    return emit_runtime_event(RuntimeEvent(kind=kind, text=text, data=data or {}))


def emit_lines(lines: Sequence[Any], *, kind: str = "lines", data: Dict[str, Any] | None = None) -> RuntimeEvent:
    """Emit a multi-line event."""
    return emit_runtime_event(
        RuntimeEvent(kind=kind, lines=tuple(str(line) for line in lines), data=data or {})
    )


def emit_blank_line() -> RuntimeEvent:
    """Emit a blank line event."""
    return emit_lines([""])


def get_runtime_events() -> List[RuntimeEvent]:
    """Return a copy of recorded runtime events."""
    return list(_RUNTIME_EVENTS)


def drain_runtime_events() -> List[RuntimeEvent]:
    """Return and clear recorded runtime events."""
    events = list(_RUNTIME_EVENTS)
    _RUNTIME_EVENTS.clear()
    return events


def clear_runtime_events() -> None:
    """Clear recorded runtime events."""
    _RUNTIME_EVENTS.clear()
