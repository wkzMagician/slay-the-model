"""Tests for innate cards and first-turn draw behavior."""

import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Avoid importing actions/__init__.py during test collection.
if "actions" not in sys.modules:
    actions_pkg = types.ModuleType("actions")
    actions_pkg.__path__ = [os.path.join(sys.path[0], "actions")]
    sys.modules["actions"] = actions_pkg

from engine.combat import Combat
from engine.game_state import game_state
from player.player import Player


class _DummyEnemy:
    """Minimal enemy stub for combat initialization tests."""

    def __init__(self):
        self._max_hp = 10
        self._hp = 10

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value):
        self._hp += value - self._max_hp
        self._max_hp = max(1, int(value))

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = max(0, min(self.max_hp, int(value)))

    def on_combat_start(self, floor: int = 1):
        return None

    def on_player_turn_start(self):
        return None

    def is_dead(self):
        return self.hp <= 0


class _StubCard:
    """Minimal card stub for card manager/combat draw tests."""

    def __init__(self, innate: bool = False):
        self.innate = innate

    def copy(self):
        return _StubCard(innate=self.innate)


def _reset_state_with_deck(deck_cards):
    game_state.__init__()
    game_state.config.debug["god_mode"] = False
    player = Player()
    player.relics = []
    player.powers = []
    player.card_manager.piles["deck"] = list(deck_cards)
    game_state.player = player
    game_state.current_floor = 1
    return player


def test_init_combat_moves_innate_cards_to_hand():
    """Innate cards should be moved from draw pile to hand at combat start."""
    player = _reset_state_with_deck(
        [_StubCard(), _StubCard(innate=True), _StubCard(), _StubCard()]
    )
    combat = Combat(enemies=[_DummyEnemy()])

    combat._init_combat()

    hand = player.card_manager.get_pile("hand")
    draw_pile = player.card_manager.get_pile("draw_pile")

    assert len(hand) == 1
    assert hand[0].innate is True
    assert all(not card.innate for card in draw_pile)
    assert len(draw_pile) == 3


def test_first_turn_draw_only_fills_to_draw_count_when_innate_exists():
    """First turn draw should fill hand to draw_count after innate setup."""
    player = _reset_state_with_deck(
        [_StubCard(innate=True), _StubCard(), _StubCard(), _StubCard(),
         _StubCard(), _StubCard()]
    )
    combat = Combat(enemies=[_DummyEnemy()])

    combat._init_combat()
    assert len(player.card_manager.get_pile("hand")) == 1

    combat._start_player_turn()
    game_state.execute_all_actions()

    # X=1 innate already in hand, Y=5 draw target => draw max(Y-X, 0)=4.
    assert len(player.card_manager.get_pile("hand")) == 5


def test_god_mode_sets_all_enemies_to_one_hp():
    """God mode should force every enemy to 1/1 HP at combat start."""
    _reset_state_with_deck([_StubCard(), _StubCard()])
    game_state.config.debug["god_mode"] = True
    enemies = [_DummyEnemy(), _DummyEnemy()]
    enemies[0].max_hp = 30
    enemies[0].hp = 23
    enemies[1].max_hp = 12
    enemies[1].hp = 7
    combat = Combat(enemies=enemies)

    combat._init_combat()

    assert all(enemy.hp == 1 for enemy in enemies)
    assert all(enemy.max_hp == 1 for enemy in enemies)
