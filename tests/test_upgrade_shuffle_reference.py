"""Actual original WarPaint/Whetstone onEquip against prepared metadata decks."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.reward import AddRelicAction
from cards.base import Card
from engine.game_state import game_state
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from relics.global_relics.common import WarPaint, Whetstone
from tests.test_special_card_reference import trace_rng
from utils.types import CardType

FIXTURE = Path(__file__).parent / "fixtures/upgrade_shuffle_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))
RELICS = {"WarPaint": WarPaint, "Whetstone": Whetstone}
COLORS = {"RED": "ironclad", "GREEN": "silent", "BLUE": "defect", "PURPLE": "watcher"}


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["relic"] + "-" + row["case"] + "-" + row["seed"])
def test_original_upgrade_relic_order_levels_calls_and_state(row, monkeypatch):
    player = game_state.player
    player.relics.clear()
    deck = []
    for value in row["deck"]:
        card = Card(card_type=CardType[value["type"]])
        card.namespace = COLORS[value["color"]]
        card.upgrade_level = value["level"]
        card.upgrade_limit = value["limit"]
        card.upgradeable = value["available"]
        card.bottled = value["bottled"]
        deck.append(card)
    player.card_manager.piles["deck"] = deck
    rng = cast(StreamRandom, get_rng("misc"))
    rng.seed(int(row["seed"]))
    calls = trace_rng(rng, monkeypatch)
    others = {name: cast(StreamRandom, get_rng(name)).export_state() for name in DOMAINS if name != "misc"}
    original = Card.upgrade
    order = []

    def upgrade(card):
        order.append(next(index for index, value in enumerate(deck) if value is card))
        return original(card)

    monkeypatch.setattr(Card, "upgrade", upgrade)
    relic = RELICS[row["relic"]]()
    game_state.add_action(AddRelicAction(relic))
    assert game_state.drive_actions() is None
    assert relic in player.relics
    assert [card.upgrade_level for card in deck] == row["levels"]
    assert [card.bottled for card in deck] == row["bottled"]
    assert order == row["upgrade_order"]
    assert calls == row["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in row["state"]} == row["state"]
    assert others == {name: cast(StreamRandom, get_rng(name)).export_state() for name in others}
    assert all(value is deck[index] for index, value in enumerate(player.card_manager.get_pile("deck")))
