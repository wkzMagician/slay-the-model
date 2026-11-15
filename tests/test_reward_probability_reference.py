"""Original room potion rewards and conditional chest gold components."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

import actions.misc as chest_actions
from actions.reward import AddRandomPotionAction
from engine.combat import Combat
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from player.player_factory import create_player
from relics.global_relics.uncommon import WhiteBeastStatue
from rooms.combat import CombatRoom
from tests.test_special_card_reference import trace_rng
from utils.compatible_random import float32
from utils.types import CombatType, RoomType

FIXTURE = Path(__file__).parent / "fixtures/reward_probability_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))
ROLES = {"IRONCLAD": "ironclad", "THE_SILENT": "silent", "DEFECT": "defect", "WATCHER": "watcher"}


@pytest.mark.parametrize("row", ROWS)
def test_actual_original_reward_probability_components(row, monkeypatch):
    if row["kind"] == "potion":
        player = create_player(ROLES[row["role"]])
        game_state.player = player
        player.relics = [WhiteBeastStatue()] if row["statue"] else []
        player.potion_limit = 99
        player.potions.clear()
        game_state.potion_drop_chance = row["chance"]
        room = CombatRoom(room_type=RoomType.ELITE if row["elite"] else RoomType.MONSTER)
        room.combat = Combat(enemies=[], combat_type=CombatType.ELITE if row["elite"] else CombatType.NORMAL)
        rng = cast(StreamRandom, get_rng("potion"))
        rng.seed(int(row["seed"]))
        calls = trace_rng(rng, monkeypatch)
        for expected_id, expected_chance in row["stages"]:
            actions = room._handle_victory()
            rewards = [action for action in actions if isinstance(action, AddRandomPotionAction)]
            assert len(rewards) == int(expected_id is not None)
            for action in rewards:
                action.execute()
                assert player.potions[-1]._original_potion_id == expected_id
            assert game_state.potion_drop_chance == expected_chance
        assert calls == row["calls"]
        state = rng.export_state()
        assert {key: state[key] for key in row["state"]} == row["state"]
    elif row["kind"] == "gold":
        rng = cast(StreamRandom, get_rng("treasure"))
        rng.seed(int(row["seed"]))
        values = []
        original = rng.random_float

        def draw(start, end):
            value = original(start, end)
            values.append(["float_range", start, end, value])
            return value

        monkeypatch.setattr(rng, "random_float", draw)
        assert chest_actions._chest_gold(row["base"]) == row["gold"]
        assert values == [[kind, float32(start), float32(end), float32(value)] for kind, start, end, value in row["calls"]]
        state = rng.export_state()
        assert {key: state[key] for key in row["state"]} == row["state"]
    else:
        rng = cast(StreamRandom, get_rng("treasure"))
        values = []
        for quantile in row["inputs"]:
            monkeypatch.setattr(rng.raw, "next_float", lambda value=float32(quantile): value)
            values.append(chest_actions._chest_gold(row["base"]))
        assert values == row["values"]
        if row["base"] == 50:
            assert {value: values[:1000].count(value) for value in range(45, 56)} == {
                45: 50, **{value: 100 for value in range(46, 55)}, 55: 50,
            }
