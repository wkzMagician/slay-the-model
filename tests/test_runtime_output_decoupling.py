from __future__ import annotations

import types


def test_emit_text_is_queued_until_explicit_flush(monkeypatch):
    from engine import runtime_presenter
    from engine.runtime_events import clear_runtime_events, emit_text, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))
    clear_runtime_events()

    emit_text("alpha", end="")

    assert rendered == []
    queued = get_runtime_events()
    assert len(queued) == 1
    assert queued[0].kind == "text"
    assert queued[0].text == "alpha"
    assert queued[0].data == {}

    flush_runtime_events()
    assert len(rendered) == 1
    assert rendered[0].kind == "text"
    assert rendered[0].text == "alpha"


def test_emit_text_preserves_joining_and_newlines(monkeypatch):
    from engine import runtime_presenter
    from engine.runtime_events import clear_runtime_events, emit_text, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event.text))
    clear_runtime_events()

    emit_text("line-1", "line-2", sep=" | ", end="")
    emit_text("tail")

    queued = get_runtime_events()
    assert [event.text for event in queued] == ["line-1 | line-2", "tail\n"]

    flush_runtime_events()
    assert rendered == ["line-1 | line-2", "tail\n"]


def test_runtime_event_order_is_preserved(monkeypatch):
    from engine import runtime_presenter
    from engine.runtime_events import clear_runtime_events, emit_text, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event.text))
    clear_runtime_events()

    emit_text("first", end="")
    emit_text("second", end="")

    assert [event.text for event in get_runtime_events()] == ["first", "second"]
    flush_runtime_events()
    assert rendered == ["first", "second"]


def test_emit_card_output_is_queued_until_explicit_flush(monkeypatch):
    from actions.card import emit_card_output
    from engine import runtime_presenter
    from engine.runtime_events import clear_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))
    clear_runtime_events()

    emit_card_output("card output", end="")

    queued = get_runtime_events()
    assert len(queued) == 1
    assert queued[0].kind == "text"
    assert queued[0].text == "card output"
    assert rendered == []

    flush_runtime_events()
    assert len(rendered) == 1
    assert rendered[0].text == "card output"


def test_gain_energy_emits_runtime_event_instead_of_print(monkeypatch):
    from actions.combat import GainEnergyAction
    from engine import runtime_presenter
    from engine.game_state import game_state
    from engine.runtime_events import clear_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))

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
        clear_runtime_events()

        result = GainEnergyAction(2).execute()

        assert getattr(result.result_type, "value", result.result_type) == "none"
        queued = get_runtime_events()
        assert queued
        assert queued[0].kind == "text"
        assert queued[0].text.startswith("Gain")
        assert rendered == []

        flush_runtime_events()
        assert len(rendered) == len(queued)
        assert [event.kind for event in rendered] == [event.kind for event in queued]
        assert [event.text for event in rendered] == [event.text for event in queued]
    finally:
        clear_runtime_events()
        game_state.player = original_player
        game_state.config = original_config


def test_end_turn_emits_runtime_event_instead_of_print(monkeypatch):
    from actions.combat import EndTurnAction
    from engine import runtime_presenter
    from engine.game_state import game_state
    from engine.runtime_events import clear_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))

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
        clear_runtime_events()

        result = EndTurnAction().execute()

        assert getattr(result.result_type, "value", result.result_type) == "none"
        queued = get_runtime_events()
        assert queued
        assert queued[0].kind == "text"
        assert rendered == []

        flush_runtime_events()
        assert len(rendered) == len(queued)
        assert [event.text for event in rendered] == [event.text for event in queued]
    finally:
        clear_runtime_events()
        game_state.current_combat = original_combat
        game_state.config = original_config


def test_shop_room_enter_emits_runtime_event_instead_of_display_action(monkeypatch):
    from engine import runtime_presenter
    from engine.game_state import game_state
    from engine.runtime_events import clear_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events
    from rooms.shop import ShopRoom

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))

    class DummyPlayer:
        def __init__(self):
            self.relics = []
            self.gold = 99

    original_player = game_state.player
    original_publish_message = game_state.publish_message
    original_config = game_state.config
    try:
        game_state.player = DummyPlayer()
        game_state.config = types.SimpleNamespace(mode="debug", debug={"print": False})
        game_state.publish_message = lambda *args, **kwargs: []
        clear_runtime_events()

        room = ShopRoom()
        result = room.enter()

        queued = get_runtime_events()
        assert queued
        assert queued[0].kind == "text"
        assert queued[0].text.endswith("\n")
        assert rendered == []
        assert result.actions

        flush_runtime_events()
        assert len(rendered) == len(queued)
        assert [event.kind for event in rendered] == [event.kind for event in queued]
        assert [event.text for event in rendered] == [event.text for event in queued]
    finally:
        clear_runtime_events()
        game_state.player = original_player
        game_state.publish_message = original_publish_message
        game_state.config = original_config


def test_event_room_empty_pool_emits_runtime_event_instead_of_display_action(monkeypatch):
    from engine import runtime_presenter
    from engine.runtime_events import clear_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events
    from rooms.event import EventRoom

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))

    clear_runtime_events()
    room = EventRoom()

    result = room._empty_pool_result()
    queued = get_runtime_events()

    assert queued
    assert queued[0].kind == "text"
    assert queued[0].text.endswith("\n")
    assert rendered == []
    assert getattr(result.result_type, "value", result.result_type) == "none"

    flush_runtime_events()
    assert len(rendered) == len(queued)
    assert [event.kind for event in rendered] == [event.kind for event in queued]
    assert [event.text for event in rendered] == [event.text for event in queued]
