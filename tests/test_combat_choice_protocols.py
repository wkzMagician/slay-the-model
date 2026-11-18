"""Prepared combat arenas exercising actual card play and input resolution."""

from typing import cast

import pytest

from actions.card_choice import ChooseAddRandomCardAction
from actions.combat_cards import PlayCardAction
from cards.base import Card
from cards.colorless.discovery import Discovery
from cards.colorless.enlightenment import Enlightenment
from cards.colorless.madness import Madness
from cards.ironclad.defend import Defend
from cards.ironclad.entrench import Entrench
from cards.silent.bullet_time import BulletTime
from enemies.act1.cultist import Cultist
from engine.combat import Combat
from engine.game_state import game_state
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from player.player_factory import create_player
from tests.test_special_card_reference import trace_rng
from utils.types import CardType


def prepare(role="ironclad", ascension=0):
    player = create_player(role, ascension=ascension)
    game_state.player = player
    player.relics.clear()
    player.base_draw_count = 0
    combat = Combat(enemies=[Cultist()])
    game_state.combat = combat
    combat._init_combat()
    assert game_state.drive_actions() is None
    for name, pile in player.card_manager.piles.items():
        if name != "deck":
            pile.clear()
    player.energy = 10
    game_state.config.debug["select_type"] = "first"
    return player, combat


def play(card):
    game_state.add_action(PlayCardAction(card))
    assert game_state.drive_actions() is None


def random_state(name):
    return cast(StreamRandom, get_rng(name)).export_state()


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("source_type", [BulletTime, Enlightenment])
def test_madness_real_play_replaces_temporary_cost_and_survives_turn(role, ascension, upgraded, source_type):
    player, combat = prepare(role, ascension)
    source, madness, target = source_type(), Madness(), Entrench()
    if upgraded:
        madness.upgrade()
    player.card_manager.piles["hand"] = [source, madness, target]
    play(source)
    assert target.cost_until_end_of_turn == (0 if source_type is BulletTime else 1)
    energy = player.energy
    play(madness)
    assert player.energy == energy - (0 if upgraded or source_type is BulletTime else 1)
    assert player.card_manager.get_card_location(madness) == "exhaust_pile"
    assert (target._cost, target.cost_until_end_of_turn, target.cost) == (0, 0, 0)
    play(target)
    assert player.energy == energy - (0 if upgraded or source_type is BulletTime else 1)
    combat._start_player_turn()
    assert game_state.drive_actions() is None
    assert target._cost == target.cost == 0
    assert target.cost_until_end_of_turn is None


@pytest.mark.parametrize("costs,expected_calls", [([], 0), ([0, -1, -2], 0), ([1], 1), ([0, 1], 5)])
def test_madness_full_hand_rejection_and_other_domains(costs, expected_calls, monkeypatch):
    player, _ = prepare()
    cards = [Card(base_cost=cost) for cost in costs]
    player.card_manager.piles["hand"] = cards
    rng = get_rng("card_random")
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    others = {name: random_state(name) for name in DOMAINS if name != "card_random"}
    Madness().on_play()
    assert len(calls) == expected_calls
    if costs == [0, 1]:
        assert [call[-1] for call in calls] == [0, 0, 0, 0, 1]
    if expected_calls:
        assert cards[-1]._cost == cards[-1].cost_until_end_of_turn == 0
    assert others == {name: random_state(name) for name in others}


@pytest.mark.parametrize("once_cost", [0, 4])
def test_madness_uses_turn_cost_before_once_override(once_cost):
    player, _ = prepare()
    temporary_free, target = Entrench(), Defend()
    temporary_free.cost_until_end_of_turn = 0
    target.cost_until_played = once_cost
    player.card_manager.piles["hand"] = [temporary_free, target]
    Madness().on_play()
    assert temporary_free._cost == 2
    assert (target._cost, target.cost_until_end_of_turn, target.cost_until_played, target.cost) == (0, 0, 0, 0)


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("hand_count", [0, 9, 10])
def test_discovery_retries_same_candidates_and_pays_once(role, ascension, upgraded, hand_count, monkeypatch):
    player, combat = prepare(role, ascension)
    discovery = Discovery()
    if upgraded:
        discovery.upgrade()
    player.card_manager.piles["hand"] = [Defend() for _ in range(hand_count)] + [discovery]
    attempts = []
    candidates = []
    answers = iter([[], [], [0]])

    def select(request):
        assert request.must_select
        assert request.max_select == 1
        assert len(request.options) == 3
        candidates.append(request.options[0].actions[0].card)
        attempts.append((tuple(id(option) for option in request.options), random_state("card_random")))
        return next(answers)

    monkeypatch.setattr(game_state, "_resolve_debug_selection", select)
    energy = player.energy
    play(discovery)
    assert len(attempts) == 3
    assert attempts[0] == attempts[1] == attempts[2]
    assert player.energy == energy - 1
    assert combat.combat_state.turn_cards_played == 1
    assert player.card_manager.get_card_location(discovery) == "exhaust_pile"
    destination = "discard_pile" if hand_count == 10 else "hand"
    assert candidates[0] is candidates[1] is candidates[2]
    assert candidates[0] in player.card_manager.get_pile(destination)
    assert len(player.card_manager.get_pile("hand")) == min(10, hand_count + 1)
    assert len(player.card_manager.get_pile("discard_pile")) == (1 if hand_count == 10 else 0)


def test_discovery_human_rejects_empty_zero_and_cancel(monkeypatch):
    player, _ = prepare()
    discovery = Discovery()
    player.card_manager.piles["hand"] = [discovery]
    game_state.config.mode = "manual"
    game_state.config.auto_select = False
    answers = iter(["", "0", "cancel", "1"])
    states = []

    def answer(prompt):
        states.append(random_state("card_random"))
        return next(answers)

    monkeypatch.setattr("builtins.input", answer)
    play(discovery)
    assert len(states) == 4
    assert all(state == states[0] for state in states)
    assert len(player.card_manager.get_pile("hand")) == 1
    assert player.energy == 9


def test_generic_typed_choice_still_allows_skip(monkeypatch):
    player, _ = prepare()
    requests = []

    def skip(request):
        requests.append(request)
        return []

    monkeypatch.setattr(game_state, "_resolve_debug_selection", skip)
    game_state.add_action(ChooseAddRandomCardAction(card_type=CardType.ATTACK))
    assert game_state.drive_actions() is None
    assert len(requests) == 1
    assert not requests[0].must_select
    assert player.card_manager.get_pile("hand") == []
