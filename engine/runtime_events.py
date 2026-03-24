"""Structured runtime events emitted by execution code."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class RuntimeEvent:
    """A structured runtime event that can be rendered by a presenter."""

    kind: str
    text: str = ""
    lines: Tuple[str, ...] = ()
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            object.__setattr__(self, "data", {})


_RUNTIME_EVENTS: List[RuntimeEvent] = []


def emit_runtime_event(event: RuntimeEvent) -> RuntimeEvent:
    """Record a runtime event without rendering it."""
    _RUNTIME_EVENTS.append(event)
    return event


def emit_text(*args: Any, sep: str = " ", end: str = "\n", kind: str = "text", data: Dict[str, Any] | None = None) -> RuntimeEvent:
    """Emit text using print-compatible concatenation semantics."""
    text = sep.join(str(arg) for arg in args) + end
    return emit_runtime_event(RuntimeEvent(kind=kind, text=text, data=data or {}))


def emit_lines(lines: List[Any], *, kind: str = "lines", data: Dict[str, Any] | None = None) -> RuntimeEvent:
    """Emit a multi-line runtime event."""
    normalized = tuple(str(line) for line in lines)
    text = "\n".join(normalized) + "\n"
    return emit_runtime_event(RuntimeEvent(kind=kind, text=text, lines=normalized, data=data or {}))


def emit_blank_line() -> RuntimeEvent:
    """Emit a blank line event."""
    return emit_text("")


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
