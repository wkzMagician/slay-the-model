"""Actual original orb helper, Confusion callback and hand-cost action."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.orb import AddOrbAction
from cards.base import Card
from cards.defect.chaos import Chaos
from engine.game_state import game_state
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from potions.global_potions import SneckoOil
from powers.definitions.confused import ConfusedPower
from tests.test_special_card_reference import trace_rng

FIXTURE = Path(__file__).parent / "fixtures/chaos_confusion_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))


def make_card(value):
    card = Card(base_cost=value["cost"])
    card.cost_until_end_of_turn = value["turn"]
    card.cost_until_played = 0 if value["free"] else None
    return card


def fields(card):
    turn = card._cost if card.cost_until_end_of_turn is None else card.cost_until_end_of_turn
    return [card._cost, turn, card.cost_until_played == 0]


def cost_calls(calls):
    # The potion's existing randint(0, 3) and JAR random(3) share this range.
    return [[0, 3, call[-1]] for call in calls]


@pytest.mark.parametrize("row", ROWS)
def test_actual_original_chaos_confusion_components(row, monkeypatch):
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(int(row["seed"]))
    calls = trace_rng(rng, monkeypatch)
    others = {name: cast(StreamRandom, get_rng(name)).export_state() for name in DOMAINS if name != "card_random"}
    power = ConfusedPower(owner=game_state.player)
    if row["kind"] == "confusion":
        card = make_card(row)
        for expected in row["stages"]:
            power.on_card_draw(card)
            assert fields(card) == expected
            assert game_state.action_queue.is_empty()
    elif row["kind"] == "chaos":
        card = Chaos()
        card._magic["orbs"] = row["count"]
        card.on_play()
        actions = [cast(AddOrbAction, action) for action in game_state.action_queue.queue if isinstance(action, AddOrbAction)]
        assert [type(action.orb).__name__.removesuffix("Orb") for action in actions] == row["orbs"]
    else:
        hand = [make_card(value) for value in row["existing"]]
        for value, expected in zip(row["drawn"], row["draw_stages"]):
            card = make_card(value)
            hand.append(card)
            power.on_card_draw(card)
            assert fields(card) == expected
        game_state.player.card_manager.piles["hand"] = hand
        SneckoOil().randomize_costs(game_state)
        # POT-002/003 retain independent base-cost/duration/negative-cost scope.
        assert [card.cost for card in hand] == [0 if free else turn for _, turn, free in row["after_oil"]]
        assert cost_calls(calls) == cost_calls(row["calls"])
    if row["kind"] != "oil_order":
        assert calls == row["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in row["state"]} == row["state"]
    assert others == {name: cast(StreamRandom, get_rng(name)).export_state() for name in others}
