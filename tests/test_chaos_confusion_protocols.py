"""Native card, potion and draw-message regressions for Chaos and Confusion."""
from typing import cast

import pytest

from actions.card import DrawCardsAction
from actions.combat_status import UsePotionAction
from actions.orb import ChannelOrbAction
from cards.colorless.forethought import Forethought
from cards.colorless.wound import Wound
from cards.defect.chaos import Chaos
from cards.ironclad.bash import Bash
from cards.ironclad.defend import Defend
from cards.ironclad.whirlwind import Whirlwind
from cards.silent.setup import Setup
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from orbs.dark import DarkOrb
from potions.global_potions import SneckoOil
from powers.base import Power
from powers.definitions.confused import ConfusedPower
from powers.definitions.no_draw import NoDrawPower
from relics.global_relics.boss import SacredBark
from tests.test_chaos_confusion_reference import ROWS
from tests.test_deferred_damage_protocols import play, prepare
from tests.test_special_card_reference import trace_rng


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("slots", [1, 3])
@pytest.mark.parametrize("seed", [0, 1, 2, 5, 42, 20261113])
def test_chaos_real_play_generates_original_orbs_and_preserves_overflow(role, ascension, upgraded, slots, seed, monkeypatch):
    player, _, combat = prepare(role, ascension)
    player.orb_manager.max_orb_slots = slots
    player.orb_manager.orbs[:] = [DarkOrb() for _ in range(slots)]
    card = Chaos()
    if upgraded:
        card.upgrade()
    expected = next(row for row in ROWS if row["kind"] == "chaos"
                    and row["seed"] == str(seed) and row["count"] == (2 if upgraded else 1))
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(seed)
    calls = trace_rng(rng, monkeypatch)
    generated = []
    original = ChannelOrbAction.execute

    def channel(action):
        generated.append(type(action.orb).__name__.removesuffix("Orb"))
        return original(action)

    monkeypatch.setattr(ChannelOrbAction, "execute", channel)
    assert play(card) is None
    assert generated == expected["orbs"]
    assert calls == expected["calls"]
    assert len(player.orb_manager.orbs) == slots
    history = combat.combat_state.orb_history
    assert sum(history.values()) == len(generated)
    assert all(history[name] == generated.count(name) for name in set(generated))
    plasma_evoked = slots == 1 and upgraded and generated[0] == "Plasma"
    assert player.energy == 9 + (2 if plasma_evoked else 0)


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("producer_type", [Setup, Forethought])
def test_actual_once_free_producer_then_confusion_draw_and_payment(role, ascension, producer_type):
    player, _, combat = prepare(role, ascension)
    target = Bash()
    player.card_manager.piles["hand"] = [target]
    assert play(producer_type()) is None
    assert player.card_manager.get_card_location(target) == "draw_pile"
    assert target.cost_until_played == 0
    player.add_power(ConfusedPower(owner=player))
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(0)
    reference = StreamRandom(0)
    expected_cost = reference.random_int(3)
    game_state.add_action(DrawCardsAction(count=1))
    assert game_state.drive_actions() is None
    assert target.cost_until_played is None
    assert target._cost == target.cost == expected_cost
    energy = player.energy
    assert play(target) is None
    assert player.energy == energy - expected_cost
    combat._start_player_turn()
    assert game_state.drive_actions() is None
    assert target._cost == target.cost == expected_cost


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("bark", [False, True])
@pytest.mark.parametrize("scenario", ["normal", "full", "blocked", "short", "shuffle"])
def test_native_oil_runs_each_confusion_callback_before_whole_hand_randomization(role, ascension, bark, scenario, monkeypatch):
    player, _, _ = prepare(role, ascension)
    player.add_power(ConfusedPower(owner=player))
    if bark:
        player.relics.append(SacredBark())
    if scenario == "blocked":
        player.add_power(NoDrawPower(owner=player))
    existing = [Bash(), Defend()] if scenario != "full" else [Defend() for _ in range(10)]
    drawn = [Defend() for _ in range(1 if scenario == "short" else 10)]
    player.card_manager.piles["hand"] = existing.copy()
    pile = "discard_pile" if scenario == "shuffle" else "draw_pile"
    player.card_manager.piles[pile] = drawn.copy()
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(42)
    calls = trace_rng(rng, monkeypatch)
    before_oil = []
    original = SneckoOil.randomize_costs

    def randomize(potion, state):
        before_oil.append(len(calls))
        assert all(card.cost_until_played is None for card in state.player.card_manager.get_pile("hand"))
        return original(potion, state)

    monkeypatch.setattr(SneckoOil, "randomize_costs", randomize)
    potion = SneckoOil()
    player.potions.append(potion)
    game_state.add_action(UsePotionAction(potion, target=player))
    assert game_state.drive_actions() is None
    count = 0 if scenario in ("full", "blocked") else 1 if scenario == "short" else min(8, 10 if bark else 5)
    assert before_oil == [count]
    assert calls[:count] == [["int", 3, call[-1]] for call in calls[:count]]
    hand = player.card_manager.get_pile("hand")
    assert len(hand) == len(existing) + count
    assert len(calls) == count + len(hand)
    assert all(call[:3] == ["int_range", 0, 3] for call in calls[count:])
    assert [card.cost for card in hand] == [call[-1] for call in calls[count:]]
    assert potion not in player.potions


def test_draw_listener_observes_each_immediate_confusion_result():
    player, _, _ = prepare()
    observed = []

    class Observer(Power):
        def on_card_draw(self, card):
            observed.append((card, card._cost))

    player.add_power(ConfusedPower(owner=player))
    player.add_power(Observer(owner=player))
    cards = [Bash(), Defend(), Bash()]
    player.card_manager.piles["draw_pile"] = list(reversed(cards))
    cast(StreamRandom, get_rng("card_random")).seed(42)
    reference = StreamRandom(42)
    expected = [reference.random_int(3) for _ in cards]
    game_state.add_action(DrawCardsAction(count=3))
    assert game_state.drive_actions() is None
    assert observed == list(zip(cards, expected))


@pytest.mark.parametrize("card_type", [Whirlwind, Wound])
def test_negative_cost_native_draw_keeps_once_free_and_random_state(card_type):
    player, _, _ = prepare()
    player.add_power(ConfusedPower(owner=player))
    card = card_type()
    card.cost_until_played = 0
    player.card_manager.piles["draw_pile"] = [card]
    rng = cast(StreamRandom, get_rng("card_random"))
    before = rng.export_state()
    original_cost = card._cost
    game_state.add_action(DrawCardsAction(count=1))
    assert game_state.drive_actions() is None
    assert rng.export_state() == before
    assert card._cost == original_cost and card.cost_until_played == 0


def test_oil_keeps_once_free_control_without_confusion():
    player, _, _ = prepare()
    card = Bash()
    card.cost_until_played = 0
    player.card_manager.piles["hand"] = [card]
    SneckoOil().randomize_costs(game_state)
    assert card.cost_until_played == 0 and card.cost == 0
