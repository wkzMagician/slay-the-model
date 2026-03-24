"""
Test P2-2 combat info display.
"""
import types


def test_combat_snapshot_uses_runtime_event_layer(monkeypatch):
    from engine import runtime_presenter
    from engine.combat import Combat
    from engine.game_state import game_state
    from engine.runtime_events import drain_runtime_events, get_runtime_events
    from engine.runtime_presenter import flush_runtime_events

    rendered = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: rendered.append(event))

    class DummyCardManager:
        def get_pile(self, name):
            return []

    class DummyPower:
        def __init__(self, name="DummyPower", amount=None, duration=-1):
            self.name = name
            self.amount = amount
            self.duration = duration
            self.localization_prefix = "powers"

        def local(self, field, **kwargs):
            return types.SimpleNamespace(resolve=lambda: f"{self.name}.{field}")

    class DummyCreature:
        def __init__(self, name="Dummy"):
            self.name = name
            self.hp = 10
            self.max_hp = 10
            self.block = 0
            self.energy = 3
            self.max_energy = 3
            self.draw_count = 5
            self.card_manager = DummyCardManager()
            self.relics = []
            self.powers = []
            self.current_intention = None

        def is_dead(self):
            return False

        def local(self, field, **kwargs):
            return types.SimpleNamespace(resolve=lambda: f"{self.name}.{field}")

    original_player = game_state.player
    original_current_combat = game_state.current_combat
    original_config = game_state.config
    try:
        player = DummyCreature("Player")
        player.powers = [DummyPower()]
        enemy = DummyCreature("Enemy")
        enemy.powers = [DummyPower()]
        game_state.player = player
        game_state.current_combat = Combat(enemies=[enemy])
        game_state.config = types.SimpleNamespace(mode="debug", debug={"print": False})
        drain_runtime_events()

        game_state.current_combat._print_combat_state()
        queued = get_runtime_events()

        assert queued
        assert queued[0].kind == "text"
        assert rendered == []

        flush_runtime_events()
        assert len(rendered) == len(queued)
        assert rendered[0].kind == queued[0].kind
    finally:
        drain_runtime_events()
        game_state.player = original_player
        game_state.current_combat = original_current_combat
        game_state.config = original_config
