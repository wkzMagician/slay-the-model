"""Actual lethal plays, potion receipts and controlled chest-gold entries."""
from typing import cast

import pytest

from actions.misc import OpenChestAction
from actions.reward import AddGoldAction, AddPotionAction, AddRandomPotionAction
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from potions.global_potions import FirePotion
from relics.global_relics.boss import Ectoplasm
from relics.global_relics.event import BloodyIdol
from relics.global_relics.uncommon import WhiteBeastStatue
from rooms.combat import CombatRoom
from rooms.treasure import TreasureRoom
from tests.test_deferred_damage_protocols import play, prepare
from tests.test_reward_probability_reference import ROWS
from tests.test_special_card_reference import trace_rng
from utils.result_types import GameTerminalState
from utils.compatible_random import float32
from utils.types import CombatType, RoomType


@pytest.mark.parametrize("role,original_role", [("ironclad", "IRONCLAD"), ("silent", "THE_SILENT"), ("defect", "DEFECT"), ("watcher", "WATCHER")])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("elite", [False, True])
@pytest.mark.parametrize("statue", [False, True])
@pytest.mark.parametrize("chance", [0, 40, 100])
@pytest.mark.parametrize("full", [False, True])
def test_actual_victory_roll_then_potion_generation_and_full_bar(role, original_role, ascension, elite, statue, chance, full, monkeypatch):
    player, enemies, combat = prepare(role, ascension, health=(6,))
    player.relics = [WhiteBeastStatue()] if statue else []
    if full:
        player.potions[:] = [FirePotion() for _ in range(player.potion_limit)]
    before_inventory = player.potions.copy()
    combat.combat_type = CombatType.ELITE if elite else CombatType.NORMAL
    room = CombatRoom(enemies=enemies, room_type=RoomType.ELITE if elite else RoomType.MONSTER)
    room.combat = combat
    game_state.current_room = room
    assert play(Strike()) is None
    assert enemies[0].hp == 0
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN
    rng = cast(StreamRandom, get_rng("potion"))
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    game_state.potion_drop_chance = chance
    expected = next(row for row in ROWS if row["kind"] == "potion" and row["role"] == original_role
                    and row["elite"] == elite and row["statue"] == statue and row["chance"] == chance
                    and row["seed"] == "0" and row["steps"] == 1)
    actions = room._handle_victory()
    assert len(calls) == 1 and calls[0][:3] == ["int_range", 0, 99]
    rewards = [action for action in actions if isinstance(action, AddRandomPotionAction)]
    selected = []
    original = AddPotionAction.execute

    def add(action):
        selected.append(action.potion._original_potion_id)
        return original(action)

    monkeypatch.setattr(AddPotionAction, "execute", add)
    for action in rewards:
        action.execute()
    assert game_state.drive_actions() is None
    expected_id, expected_chance = expected["stages"][0]
    assert selected == ([] if expected_id is None else [expected_id])
    assert game_state.potion_drop_chance == expected_chance
    assert calls == expected["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in expected["state"]} == expected["state"]
    if full:
        assert player.potions == before_inventory
    else:
        assert len(player.potions) == int(expected_id is not None)


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("size,base", [("small", 25), ("medium", 50), ("large", 75)])
@pytest.mark.parametrize("seed", [0, 42])
@pytest.mark.parametrize("held", ["none", "ectoplasm", "bloody_idol"])
def test_open_chest_gold_and_existing_receipt_modifiers(role, ascension, size, base, seed, held, monkeypatch):
    player, _, _ = prepare(role, ascension)
    if held == "ectoplasm":
        player.relics = [Ectoplasm()]
    elif held == "bloody_idol":
        player.relics = [BloodyIdol()]
    player.hp = player.max_hp - 10
    original_hp, original_gold = player.hp, player.gold
    room = TreasureRoom()
    room.chest_type = size
    game_state.current_room = room
    rng = cast(StreamRandom, get_rng("treasure"))
    rng.seed(seed)
    # Explicit gold/tier gates isolate the conditional amount protocol.
    monkeypatch.setattr(rng, "random", lambda: 0.1)
    observed = []
    original = rng.random_float

    def amount(start, end):
        value = original(start, end)
        observed.append(["float_range", start, end, value])
        return value

    monkeypatch.setattr(rng, "random_float", amount)
    OpenChestAction(room).execute()
    expected = next(row for row in ROWS if row["kind"] == "gold" and row["base"] == base and row["seed"] == str(seed))
    gold = cast(AddGoldAction, next(action for action in game_state.action_queue.queue if isinstance(action, AddGoldAction)))
    assert gold.amount == expected["gold"]
    expected_calls = [[kind, float32(start), float32(end), float32(value)] for kind, start, end, value in expected["calls"]]
    assert observed == expected_calls
    before = rng.export_state()
    OpenChestAction(room).execute()
    assert rng.export_state() == before and observed == expected_calls
    # Exercise the selected receipt independently from the other chest rewards.
    game_state.action_queue.clear()
    gold.execute()
    assert game_state.drive_actions() is None
    assert player.gold == original_gold + (0 if held == "ectoplasm" else expected["gold"])
    assert player.hp == original_hp + (5 if held == "bloody_idol" else 0)


@pytest.mark.parametrize("size", ["small", "medium", "large"])
def test_chest_without_gold_skips_amount_draw(size, monkeypatch):
    prepare()
    room = TreasureRoom()
    room.chest_type = size
    rng = cast(StreamRandom, get_rng("treasure"))
    monkeypatch.setattr(rng, "random", lambda: 0.99)
    calls = []
    original = rng.random_float

    def amount(start, end):
        calls.append([start, end])
        return original(start, end)

    monkeypatch.setattr(rng, "random_float", amount)
    OpenChestAction(room).execute()
    assert calls == []
    assert not any(isinstance(action, AddGoldAction) for action in game_state.action_queue.queue)
