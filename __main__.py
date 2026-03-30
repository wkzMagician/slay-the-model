# -*- coding: utf-8 -*-
"""
Entry point for Slay the Model game.
Supports both TUI mode (default) and CLI mode (--no-tui flag).
"""
import sys
import os

# Fix Windows console encoding BEFORE any imports that might print
# if sys.platform == 'win32':
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#     sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
from engine.game_flow import GameFlow
from engine.game_state import game_state
from engine.runtime_context import configure_noninteractive_cli_mode


def _import_potions():
    """Import potions to register them in the registry."""
    import potions


def _import_powers():
    """Import powers to register them in the registry."""
    from powers import definitions


def _import_relics():
    """Import relics to register them in the registry."""
    import relics


def _is_interactive_stdin():
    """Return True when stdin can accept interactive input."""
    try:
        return bool(sys.stdin and sys.stdin.isatty())
    except (AttributeError, OSError, ValueError):
        return False


def run_cli_mode():
    """Run game in traditional CLI mode (no TUI)."""
    try:
        if not _is_interactive_stdin():
            configure_noninteractive_cli_mode(game_state)
        _import_potions()
        _import_powers()
        _import_relics()
        game = GameFlow()
        game.start_game(game_state)
    except KeyboardInterrupt:
        from localization import t
        print(f"\n{t('ui.game_interrupted', default='Game interrupted by user.')}")
    except Exception as e:
        from localization import t
        print(f"\n{t('ui.game_error', default=f'Game error: {e}', error=e)}")
        import traceback
        traceback.print_exc()


def run_tui_mode():
    """Run game in TUI mode with three-panel layout."""
    try:
        # Import all game components first
        _import_potions()
        _import_powers()
        _import_relics()
        
        # Import TUI app
        from tui.app import SlayTheModelApp
        
        # Create and run TUI app
        app = SlayTheModelApp()
        
        # Set AI mode based on config (mode is 'ai' or 'debug' for non-human modes)
        mode = game_state.config.mode
        is_ai_mode = mode in ('ai', 'debug')
        app.set_ai_mode(is_ai_mode)
        
        app.run()
        
    except ImportError as e:
        print(f"TUI not available: {e}")
        print("Falling back to CLI mode...")
        print("Try installing textual: pip install textual")
        run_cli_mode()
    except KeyboardInterrupt:
        from localization import t
        print(f"\n{t('ui.game_interrupted', default='Game interrupted by user.')}")
    except Exception as e:
        from localization import t
        print(f"\n{t('ui.game_error', default=f'Game error: {e}', error=e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Slay the Model - A roguelike deck-builder game"
    )
    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="Run in traditional CLI mode without TUI panels"
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Force TUI mode (default)"
    )
    
    args = parser.parse_args()
    
    if args.no_tui:
        run_cli_mode()
    else:
        run_tui_mode()


if __name__ == "__main__":
    main()
