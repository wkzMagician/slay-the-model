import types

from engine.runtime_context import configure_noninteractive_cli_mode, is_stdin_interactive


class _DummyStdin:
    def __init__(self, interactive):
        self._interactive = interactive

    def isatty(self):
        return self._interactive


class _DummyConfig:
    def __init__(self):
        self.mode = "human"
        self.auto_select = False
        self.debug = {"select_type": "random"}


class _DummyGameState:
    def __init__(self):
        self.config = _DummyConfig()


def test_is_stdin_interactive_uses_isatty():
    assert is_stdin_interactive(_DummyStdin(True)) is True
    assert is_stdin_interactive(_DummyStdin(False)) is False


def test_configure_noninteractive_cli_mode_switches_to_debug():
    game_state = _DummyGameState()

    switched = configure_noninteractive_cli_mode(game_state, stdin=_DummyStdin(False))

    assert switched is True
    assert game_state.config.mode == "debug"
    assert game_state.config.auto_select is True
    assert game_state.config.debug["select_type"] == "first"


def test_configure_noninteractive_cli_mode_keeps_interactive_mode():
    game_state = _DummyGameState()

    switched = configure_noninteractive_cli_mode(game_state, stdin=_DummyStdin(True))

    assert switched is False
    assert game_state.config.mode == "human"
    assert game_state.config.auto_select is False
    assert game_state.config.debug["select_type"] == "random"
