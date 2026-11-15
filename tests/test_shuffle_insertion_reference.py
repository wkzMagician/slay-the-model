"""Original CardGroup and shuffle actions with an explicit Soul transfer boundary."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.card_lifecycle import AddCardAction
from actions.card_shuffle import queue_active_shuffle
from cards.base import Card
from engine.game_state import game_state
from engine.messages import ShuffleMessage
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from tests.test_special_card_reference import trace_rng
from utils.types import PilePosType

FIXTURE = Path(__file__).parent / "fixtures/shuffle_insertion_reference.json.gz"
ROWS = json.loads(gzip.decompress(FIXTURE.read_bytes()))


def normalized_calls(calls):
    return [["int", call[2], call[3]] if call[0] == "int_range" else call for call in calls]


@pytest.mark.parametrize("row", ROWS)
def test_actual_original_shuffle_and_insertion(row, monkeypatch):
    player = game_state.player
    player.relics.clear()
    manager = player.card_manager
    labels = {}

    def cards(prefix, count):
        result = [Card() for _ in range(count)]
        labels.update({id(card): prefix + str(index) for index, card in enumerate(result)})
        return result

    def ids(pile):
        return [labels[id(card)] for card in pile]

    rngs = {name: cast(StreamRandom, get_rng(name)) for name in ("card_random", "shuffle")}
    for name, delta in [("card_random", 0), ("shuffle", 1)]:
        rngs[name].seed(int(row["seed"]) + delta)
    calls = {name: trace_rng(rng, monkeypatch) for name, rng in rngs.items()}
    others = {name: cast(StreamRandom, get_rng(name)).export_state() for name in DOMAINS if name not in rngs}
    if row["kind"] == "insert":
        manager.piles["draw_pile"] = cards("I", row["size"])
        additions = cards("N", row["count"])
        for card, expected in zip(additions, row["stages"]):
            AddCardAction(card, "draw_pile", position=PilePosType.RANDOM).execute()
            assert ids(manager.get_pile("draw_pile")) == expected
    else:
        for pile, prefix, key in [("draw_pile", "D", "draw"), ("discard_pile", "C", "discard"), ("hand", "H", "hand")]:
            manager.piles[pile] = cards(prefix, row[key])
        moves = []
        notices = []
        shuffles = []
        original_move = manager.move_to
        original_publish = game_state.publish_message
        original_shuffle = rngs["shuffle"].shuffle

        def move(card, dst, src=None, pos=None):
            moves.append(["discard" if src == "discard_pile" else src, labels[id(card)]])
            return original_move(card, dst, src, pos)

        def publish(message, *args, **kwargs):
            if isinstance(message, ShuffleMessage):
                notices.append([rngs["card_random"].counter, rngs["shuffle"].counter])
            return original_publish(message, *args, **kwargs)

        def shuffle(pile):
            before = ids(pile)
            result = original_shuffle(pile)
            shuffles.append([before, ids(pile)])
            return result

        monkeypatch.setattr(manager, "move_to", move)
        monkeypatch.setattr(game_state, "publish_message", publish)
        monkeypatch.setattr(rngs["shuffle"], "shuffle", shuffle)
        if row["kind"] == "reboot" or row["discard"]:
            queue_active_shuffle(include_hand=row["kind"] == "reboot")
        assert game_state.drive_actions() is None
        assert ids(manager.get_pile("draw_pile")) == row["draw_after"]
        assert ids(manager.get_pile("hand")) == row["hand_after"]
        assert ids(manager.get_pile("discard_pile")) == row["discard_after"]
        assert moves == row["moves"]
        assert notices == row["notices"]
        if shuffles:
            assert shuffles[0] == [["C" + str(index) for index in range(row["discard"])],
                                   [card for source, card in row["moves"] if source == "discard"]]
            assert shuffles[1] == [row["stages"][-2][1], row["draw_after"]]
    for name, prefix in [("card_random", "card"), ("shuffle", "shuffle")]:
        assert normalized_calls(calls[name]) == row[prefix + "_calls"]
        state = rngs[name].export_state()
        assert {key: state[key] for key in row[prefix + "_state"]} == row[prefix + "_state"]
    assert others == {name: cast(StreamRandom, get_rng(name)).export_state() for name in others}
