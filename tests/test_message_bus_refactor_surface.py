from engine.combat import Combat
from engine.message_bus import MessageBus


def test_message_bus_public_surface_still_exports_runtime_handlers():
    exports = [
        MessageBus,
    ]

    for exported in exports:
        assert exported is not None


def test_combat_message_participants_include_hand_when_requested(monkeypatch):
    captured = {}

    class StubGameState:
        def message_participants(self, enemies=None, include_hand=False, hand=None):
            captured['enemies'] = enemies
            captured['include_hand'] = include_hand
            captured['hand'] = hand
            return ['participants']

    monkeypatch.setattr('engine.game_state.game_state', StubGameState())

    hand = [object()]
    enemies = [object()]
    combat = Combat(enemies=[])

    assert combat._message_participants(enemies, include_hand=True, hand=hand) == ['participants']
    assert captured == {
        'enemies': enemies,
        'include_hand': True,
        'hand': hand,
    }
