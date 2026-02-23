# -*- coding: utf-8 -*-
"""
TUI-aware print utility - routes output to TUI panel when available.
"""
import sys
from typing import Any


def tui_print(*args, **kwargs):
    """
    Print that routes to TUI output panel when available, otherwise uses standard print.
    
    Usage: Replace `print(...)` with `from tui.print_utils import tui_print; tui_print(...)`
    
    This ensures all game output appears in the TUI output panel when running
    in TUI mode, while preserving standard CLI behavior in fallback mode.
    """
    # Try to get TUI app
    try:
        from tui import get_app, is_tui_mode
        app = get_app()
        
        if app is not None and is_tui_mode():
            # Build message from args
            sep = kwargs.get('sep', ' ')
            end = kwargs.get('end', '\n')
            message = sep.join(str(arg) for arg in args)
            if end:
                message = message.rstrip('\n')  # add_output handles newlines
            
            # Route to TUI output panel
            app.add_output(message)
            return
    except ImportError:
        pass
    
    # Fallback to standard print
    print(*args, **kwargs)


def tui_print_debug(*args, **kwargs):
    """
    Debug print that only outputs when in debug mode.
    Routes through TUI when available.
    """
    try:
        from engine.game_state import game_state
        mode = game_state.config.get("mode", "debug")
        if mode == "debug":
            tui_print(*args, **kwargs)
    except ImportError:
        tui_print(*args, **kwargs)
