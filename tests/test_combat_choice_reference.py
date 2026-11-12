"""Actual original Madness and Discovery updates with prepared UI state."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.card_choice import ChooseAddRandomCardAction
from actions.display import InputRequestAction
from cards.base import Card
from cards.colorless.discovery import Discovery
from cards.colorless.madness import Madness
from engine.card_pools import original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from tests.test_special_card_reference import trace_rng
from utils.types import CardType

FIXTURE = Path(__file__).parent / "fixtures/combat_choice_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))
COLORS = {"RED": "ironclad", "GREEN": "silent", "BLUE": "defect", "PURPLE": "watcher"}


@pytest.mark.parametrize("row", ROWS)
def test_actual_original_combat_choice(row, monkeypatch):
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(int(row["seed"]))
    calls = trace_rng(rng, monkeypatch)
    if row["kind"] == "madness":
        hand = []
        for value in row["hand"]:
            card = Card(base_cost=value["cost"])
            card.cost_until_end_of_turn = value["turn"]
            card.cost_until_played = 0 if value["free"] else None
            hand.append(card)
        game_state.player.card_manager.piles["hand"] = hand
        Madness().on_play()
        after = [
            [card._cost,
             card._cost if card.cost_until_end_of_turn is None else card.cost_until_end_of_turn,
             card.cost_until_played is not None]
            for card in hand
        ]
        assert after == row["after"]
        assert (calls[-1][-1] if calls else None) == row["target"]
        if row["target"] is not None:
            assert hand[row["target"]].cost_until_end_of_turn == 0
    else:
        game_state.player.namespace = COLORS[row["color"]]
        cast(StreamRandom, get_rng("card")).seed(int(row["seed"]) + 1)
        if row["variant"] == "default":
            Discovery().on_play()
            producer = next(
                action for action in game_state.action_queue.queue
                if isinstance(action, ChooseAddRandomCardAction)
            )
        else:
            producer = ChooseAddRandomCardAction(card_type=CardType[row["variant"]])
        producer.execute()
        request = cast(InputRequestAction, next(
            action for action in game_state.action_queue.queue
            if isinstance(action, InputRequestAction)
        ))
        assert request.must_select is not row["skippable"]
        assert request.max_select == 1
        assert [original_id(option.actions[0].card) for option in request.options] == row["cards"]
    assert calls == row["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in row["state"]} == row["state"]
