# -*- coding: utf-8 -*-
"""TUI (Terminal User Interface) module for Slay the Model."""

_tui_app = None

def get_app():
    """Get the current TUI app instance."""
    return _tui_app

def set_app(app):
    """Set the current TUI app instance."""
    global _tui_app
    _tui_app = app

def is_tui_mode():
    """Check if TUI mode is active."""
    return _tui_app is not None
