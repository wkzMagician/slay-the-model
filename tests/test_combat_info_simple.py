"""
Test P2-2 combat info display.
"""
import types


def test_combat_snapshot_uses_runtime_event_layer(capsys, monkeypatch):
    from engine import runtime_presenter
    from engine.combat import Combat
    from engine.game_state import game_state
    from engine.runtime_events import drain_runtime_events

    events = []
    monkeypatch.setattr(runtime_presenter, "render_runtime_event", lambda event: events.append(event))

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
            self.current_intention = None
            self.relics = []
            self.powers = []

        def is_dead(self):
            return False

        def local(self, field, **kwargs):
            return types.SimpleNamespace(resolve=lambda: f"{self.name}.{field}")

    original_player = game_state.player
    original_current_combat = game_state.current_combat
    original_config = game_state.config
    original_mode = getattr(game_state.config, "mode", None) if game_state.config else None
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

        assert capsys.readouterr().out == ""
        assert events, "expected runtime events instead of direct combat printing"
    finally:
        drain_runtime_events()
        game_state.player = original_player
        game_state.current_combat = original_current_combat
        game_state.config = original_config


