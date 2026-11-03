"""Opening expectations from the fixed original character/dungeon loadouts."""
import importlib
from itertools import permutations

import pytest

from config.game_config import GameConfig
from engine.game_state import GameState
from player.player_factory import create_player


ROLES = ["Ironclad", "Silent", "Defect", "Watcher"]


@pytest.mark.parametrize("character,ascension,hp,max_hp,slots,size", [
    ("Ironclad", 0, 80, 80, 3, 10),
    ("Ironclad", 5, 80, 80, 3, 10),
    ("Ironclad", 6, 72, 80, 3, 10),
    ("Ironclad", 9, 72, 80, 3, 10),
    ("Ironclad", 10, 72, 80, 3, 11),
    ("Ironclad", 11, 72, 80, 2, 11),
    ("Ironclad", 13, 72, 80, 2, 11),
    ("Ironclad", 14, 68, 75, 2, 11),
    ("Ironclad", 20, 68, 75, 2, 11),
    ("Silent", 14, 59, 66, 2, 13),
    ("Defect", 14, 64, 71, 2, 11),
    ("Watcher", 14, 61, 68, 2, 11),
])
def test_normal_game_state_opening(monkeypatch, character, ascension, hp, max_hp, slots, size):
    config = GameConfig(character=character, ascension=ascension, seed=123, mode="debug")
    monkeypatch.setattr(GameConfig, "load", staticmethod(lambda _: config))
    state = GameState()
    player = state.player
    for _ in range(2):
        state.begin_run()
        assert (player.hp, player.max_hp) == (hp, max_hp)
        assert player.potion_limit == slots
        assert len(player.deck) == size
        assert sum(type(c).__name__ == "AscendersBane" for c in player.deck) == (ascension >= 10)


@pytest.mark.parametrize("order", list(permutations(ROLES)))
def test_repeated_character_creation_keeps_card_color(order):
    for character in (*order, *reversed(order)):
        player = create_player(character)
        assert all(c.namespace == character.lower() for c in player.deck)
        assert player.orb_manager.max_orb_slots == (3 if character == "Defect" else 0)
        assert player.base_orb_slots == player.orb_manager.max_orb_slots


@pytest.mark.parametrize("character", ROLES)
@pytest.mark.parametrize("ascension", [0, 6, 10, 11, 14, 20])
def test_new_player_does_not_share_bane_or_starting_cards(character, ascension):
    first = create_player(character, ascension=ascension)
    second = create_player(character, ascension=ascension)
    assert len(first.deck) == len(second.deck)
    assert all(a is not b for a, b in zip(first.deck, second.deck))
    assert sum(type(c).__name__ == "AscendersBane" for c in second.deck) == (ascension >= 10)


def test_event_imports_cannot_change_next_run_starters(monkeypatch):
    from engine.game_state import game_state
    from events.ancient_writing import AncientWriting
    from events import a_note_for_yourself as note
    monkeypatch.setattr(note, "_load_stored_card", lambda: None)

    for character in ROLES:
        game_state.player = create_player(character)
        AncientWriting().trigger()
        importlib.import_module("events.vampires")
        from actions.card_transform import RemoveAllStrikesAction
        RemoveAllStrikesAction().execute()
        note._received_card()
        for next_character in ROLES:
            player = create_player(next_character)
            assert all(c.namespace == next_character.lower() for c in player.deck)


@pytest.mark.parametrize("character", ROLES)
def test_later_relic_capacity_changes_survive_begin_run(character):
    from engine.game_state import game_state
    from actions.reward import AddRelicAction
    from relics.global_relics.common import PotionBelt
    from relics.global_relics.shop import PrismaticShard

    game_state.player = create_player(character, ascension=11)
    AddRelicAction(PotionBelt()).execute()
    AddRelicAction(PrismaticShard()).execute()
    game_state.begin_run()
    assert game_state.player.potion_limit == 4
    assert game_state.player.base_orb_slots == (3 if character == "Defect" else 1)
    assert game_state.player.orb_manager.max_orb_slots == game_state.player.base_orb_slots
