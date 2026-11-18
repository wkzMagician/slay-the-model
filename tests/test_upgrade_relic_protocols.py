"""Native relic acquisition with actual cards and isolated shared-action calls."""
from typing import cast

import pytest

from actions.card_transform import UpgradeCardAction, UpgradeRandomCardAction
from actions.reward import AddRelicAction
from cards.ironclad.defend import Defend
from cards.ironclad.searing_blow import SearingBlow
from cards.ironclad.shrug_it_off import ShrugItOff
from cards.ironclad.strike import Strike
from cards.ironclad.twin_strike import TwinStrike
from cards.silent.defend import Defend as SilentDefend
from enemies.act1.cultist import Cultist
from engine.combat import Combat
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from player.player_factory import create_player
from relics.global_relics.common import WarPaint, Whetstone
from relics.global_relics.uncommon import BottledFlame, BottledLightning
from tests.test_special_card_reference import trace_rng
from tests.test_upgrade_shuffle_reference import ROWS


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("relic_type,card_type,wrong_type,attribute,value", [
    (WarPaint, Defend, Strike, "block", 8),
    (Whetstone, Strike, Defend, "damage", 9),
])
@pytest.mark.parametrize("count", [0, 1, 2, 3, 10])
@pytest.mark.parametrize("seed", [0, 42, 20261112])
def test_native_obtain_upgrades_expected_objects_in_order(role, ascension, relic_type, card_type,
                                                        wrong_type, attribute, value, count, seed, monkeypatch):
    player = create_player(role, ascension=ascension)
    player.relics.clear()
    game_state.player = player
    game_state.ascension = ascension
    cards = [card_type() for _ in range(count)]
    upgraded = card_type()
    upgraded.upgrade()
    wrong = wrong_type()
    deck = [wrong, *cards, upgraded]
    player.card_manager.piles["deck"] = deck.copy()
    before = {id(card): (card.upgrade_level, card.damage, card.block) for card in deck}
    case = {0: "empty", 1: "one", 2: "two", 3: "three", 10: "ten"}[count]
    expected = next(row for row in ROWS if row["relic"] == relic_type.__name__
                    and row["seed"] == str(seed) and row["case"] == case)
    rng = cast(StreamRandom, get_rng("misc"))
    rng.seed(seed)
    calls = trace_rng(rng, monkeypatch)
    order = []
    original = UpgradeCardAction.execute

    def execute(action):
        order.append(next(index for index, card in enumerate(cards) if card is action.card))
        return original(action)

    monkeypatch.setattr(UpgradeCardAction, "execute", execute)
    relic = relic_type()
    game_state.add_action(AddRelicAction(relic))
    assert game_state.drive_actions() is None
    assert order == expected["upgrade_order"]
    assert calls == expected["calls"]
    state = rng.export_state()
    assert {key: state[key] for key in expected["state"]} == expected["state"]
    assert relic in player.relics and relic.idstr in game_state.obtained_relics
    assert len(player.card_manager.get_pile("deck")) == len(deck)
    assert all(card is deck[index] for index, card in enumerate(player.card_manager.get_pile("deck")))
    for index, card in enumerate(cards):
        assert card.upgrade_level == int(index in order)
        if index in order:
            assert getattr(card, attribute) == value
            assert "+" in str(card.display_name)
        else:
            assert (card.upgrade_level, card.damage, card.block) == before[id(card)]
    for card in (wrong, upgraded):
        assert (card.upgrade_level, card.damage, card.block) == before[id(card)]


@pytest.mark.parametrize("relic_type,card_type,bottle_type,attribute,value", [
    (WarPaint, ShrugItOff, BottledLightning, "block", 11),
    (Whetstone, TwinStrike, BottledFlame, "damage", 7),
])
def test_bottled_upgrade_keeps_binding_and_upgraded_combat_copy(relic_type, card_type, bottle_type, attribute, value):
    player = create_player("ironclad")
    game_state.player = player
    target = card_type()
    target.bottled = True
    bottle = bottle_type()
    bottle.selected_card = target
    player.relics = [bottle]
    player.card_manager.piles["deck"] = [target]
    game_state.add_action(AddRelicAction(relic_type()))
    assert game_state.drive_actions() is None
    assert bottle.selected_card is target and target.bottled
    assert target.upgrade_level == 1 and getattr(target, attribute) == value
    player.base_draw_count = 1
    combat = Combat(enemies=[Cultist()])
    game_state.combat = combat
    combat._init_combat()
    assert game_state.drive_actions() is None
    hand = player.card_manager.get_pile("hand")
    assert len(hand) == 1 and hand[0] is not target
    assert hand[0].bottled and hand[0].upgrade_level == 1
    assert getattr(hand[0], attribute) == value
    assert bottle.selected_card is target


def test_cross_color_skill_and_multi_upgrade_attack_remain_eligible():
    player = game_state.player
    player.relics.clear()
    foreign = SilentDefend()
    multi = SearingBlow()
    multi.upgrade()
    player.card_manager.piles["deck"] = [foreign, multi]
    for relic in (WarPaint(), Whetstone()):
        game_state.add_action(AddRelicAction(relic))
        assert game_state.drive_actions() is None
    assert foreign.upgrade_level == 1 and foreign.block == 8
    assert multi.upgrade_level == 2 and multi.damage == 21


@pytest.mark.parametrize("count", [0, 1, 2, 5])
def test_shared_action_default_retains_sample_protocol(count, monkeypatch):
    deck = [Defend() for _ in range(count)]
    game_state.player.card_manager.piles["deck"] = deck
    rng = cast(StreamRandom, get_rng("misc"))
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    game_state.add_action(UpgradeRandomCardAction())
    assert game_state.drive_actions() is None
    expected_index = 2 if count == 5 else 0
    assert calls == ([] if count == 0 else [["int", count - 1, expected_index]])
    assert sum(card.upgrade_level for card in deck) == min(count, 1)


def test_shuffle_action_respects_explicit_namespace_and_upgrade_count():
    local = Defend()
    foreign = SilentDefend()
    game_state.player.card_manager.piles["deck"] = [local, foreign]
    game_state.add_action(UpgradeRandomCardAction(count=1, namespace="silent", selection_kind="shuffle"))
    assert game_state.drive_actions() is None
    assert local.upgrade_level == 0 and foreign.upgrade_level == 1


@pytest.mark.parametrize("count", [0, 1, 2, 5])
def test_shuffle_action_count_boundaries(count, monkeypatch):
    cards = [Defend() for _ in range(3)]
    game_state.player.card_manager.piles["deck"] = cards
    rng = cast(StreamRandom, get_rng("misc"))
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    game_state.add_action(UpgradeRandomCardAction(count=count, selection_kind="shuffle"))
    assert game_state.drive_actions() is None
    assert sum(card.upgrade_level for card in cards) == min(3, count)
    assert len(calls) == 1 and calls[0][0] == "long"


def test_shuffle_action_rejects_negative_count():
    with pytest.raises(ValueError, match="nonnegative"):
        UpgradeRandomCardAction(count=-1, selection_kind="shuffle")
