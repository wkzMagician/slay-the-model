import types

import pytest


def test_gain_energy_emits_runtime_event_instead_of_print(capsys, monkeypatch):
    from actions.combat import GainEnergyAction
    from engine import runtime_presenter
    from engine.runtime_events import drain_runtime_events
    from engine.game_state import game_state

    events = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: events.append(event))

    class DummyPlayer:
        def __init__(self):
            self.energy = 0
            self.max_energy = 3

        def gain_energy(self, amount):
            self.energy += amount

    original_player = game_state.player
    original_config = game_state.config
    try:
        game_state.player = DummyPlayer()
        game_state.config = types.SimpleNamespace(mode="debug", debug={"print": False})
        drain_runtime_events()

        result = GainEnergyAction(2).execute()

        assert getattr(result.result_type, "value", result.result_type) == "none"
        assert capsys.readouterr().out == ""
        assert events, "expected runtime events to be emitted instead of direct printing"
    finally:
        drain_runtime_events()
        game_state.player = original_player
        game_state.config = original_config


def test_end_turn_emits_runtime_event_instead_of_print(capsys, monkeypatch):
    from actions.combat import EndTurnAction
    from engine import runtime_presenter
    from engine.runtime_events import drain_runtime_events
    from engine.game_state import game_state

    events = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: events.append(event))

    class DummyCombatState:
        def __init__(self):
            self.current_phase = "player_action"

    class DummyCombat:
        def __init__(self):
            self.combat_state = DummyCombatState()

    original_combat = game_state.current_combat
    original_config = game_state.config
    try:
        game_state.current_combat = DummyCombat()
        game_state.config = types.SimpleNamespace(mode="debug", debug={"print": False})
        drain_runtime_events()

        result = EndTurnAction().execute()

        assert getattr(result.result_type, "value", result.result_type) == "none"
        assert capsys.readouterr().out == ""
        assert events, "expected runtime events to be emitted instead of direct printing"
    finally:
        drain_runtime_events()
        game_state.current_combat = original_combat
        game_state.config = original_config

