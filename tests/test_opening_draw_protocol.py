"""Prepared decks through real combat startup; original CardGroup/room rules."""
from copy import copy
import json
from pathlib import Path

import pytest

from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from cards.ironclad.inflame import Inflame
from cards.silent.backstab import Backstab
from cards.colorless.void import Void
from enemies.act1.cultist import Cultist
from engine.combat import Combat
from engine.game_state import game_state
from engine.messages import CardDrawnMessage, CardPlayedMessage
from engine.random_streams import RandomStreams
from player.player import Player
from relics.character.silent import RingOfTheSnake, NinjaScroll
from relics.character.watcher import PureWater, HolyWater
from relics.global_relics.common import BagOfPreparation, Anchor, Lantern
from relics.global_relics.boss import SneckoEye
from relics.global_relics.uncommon import BottledFlame, BottledLightning, BottledTornado
from utils.result_types import GameTerminalState


class DrawObserver:
    priority = 0

    def __init__(self):
        self.draws = []
        self.blocks = []
        self.confused = []

    def handles(self, message):
        return isinstance(message, CardDrawnMessage)

    def handle(self, message):
        self.draws.append(message.card)
        self.blocks.append(message.owner.block)
        self.confused.append(any(type(p).__name__ == "ConfusedPower" for p in message.owner.powers))
        return []


def prepare(deck, relics=(), seed=523):
    player = Player(max_hp=80)
    player.deck = deck
    player.relics = list(relics)
    game_state.player = player
    game_state.random_streams = RandomStreams(seed)
    observer = DrawObserver()
    game_state.message_bus.register(observer)
    return player, Combat([Cultist()]), observer


def first_decision(combat):
    """Run Combat.start, stopping at the actual first player decision boundary."""
    combat._execute_player_action_phase = lambda: GameTerminalState.GAME_EXIT
    assert combat.start() == GameTerminalState.GAME_EXIT


@pytest.mark.parametrize("count", [0, 1, 2, 5, 7, 10, 11])
@pytest.mark.parametrize("bonus", [False, True])
def test_innate_draws_notify_and_leave_overflow_in_draw_pile(count, bonus):
    deck = [Backstab() for _ in range(count)] + [Defend() for _ in range(6)]
    player, combat, observed = prepare(deck, [BagOfPreparation()] if bonus else [])
    first_decision(combat)
    expected = min(10, len(deck), max(5, count) + (2 if bonus else 0))
    hand = player.card_manager.get_pile("hand")
    assert len(hand) == expected
    assert observed.draws == hand
    assert sum(c.innate for c in hand) == min(count, 10)
    assert len(player.card_manager.get_pile("discard_pile")) == 0
    assert len(player.card_manager.get_pile("draw_pile")) == len(deck) - expected
    assert len(player.deck) == len(deck)
    assert all(c in deck for c in player.deck)


@pytest.mark.parametrize("relic_class,normal,generated", [
    (BagOfPreparation, 7, 0), (RingOfTheSnake, 7, 0),
    (PureWater, 5, 1), (HolyWater, 5, 3), (NinjaScroll, 5, 3),
])
@pytest.mark.parametrize("size", [3, 6, 20])
def test_opening_relics_do_not_replace_base_draws(relic_class, normal, generated, size):
    player, combat, observed = prepare([Defend() for _ in range(size)], [relic_class()])
    first_decision(combat)
    hand = player.card_manager.get_pile("hand")
    assert len(observed.draws) == min(size, normal)
    assert sum(type(c) is Defend for c in hand) == min(size, normal)
    assert len(hand) == min(size, normal) + generated


@pytest.mark.parametrize("relic_class,card_class", [
    (BottledFlame, Strike), (BottledLightning, Defend), (BottledTornado, Inflame),
])
def test_bottle_draws_exact_selected_combat_copy_once(relic_class, card_class):
    twins = [card_class(), card_class()]
    chosen = twins[1]
    bottle = relic_class()
    bottle.selected_card = chosen
    chosen.bottled = True
    deck = twins + [Defend() for _ in range(12)]
    player, combat, observed = prepare(deck, [bottle])
    first_decision(combat)
    assert len(observed.draws) == 5
    assert getattr(observed.draws[0], "origin_card") is chosen
    assert observed.draws[0] is not chosen
    all_combat = sum((player.card_manager.get_pile(p) for p in ("hand", "draw_pile", "discard_pile", "exhaust_pile")), [])
    assert len(all_combat) == len(deck)
    assert sum(getattr(c, "origin_card") is chosen for c in all_combat) == 1
    assert all(c is not chosen for c in all_combat)


def test_base_draw_precedes_bonus_and_anchor_actions():
    player, combat, observed = prepare([Defend() for _ in range(20)], [Anchor(), BagOfPreparation()])
    first_decision(combat)
    assert len(observed.draws) == 7
    assert observed.blocks == [0] * 5 + [10] * 2
    assert player.block == 10


def test_snecko_confusion_precedes_all_opening_draws():
    _player, combat, observed = prepare([Defend() for _ in range(20)], [SneckoEye()])
    first_decision(combat)
    assert len(observed.draws) == 7
    assert all(observed.confused)


@pytest.mark.parametrize("count", [5, 6, 7, 11])
def test_snecko_hand_size_counts_its_two_draws_before_innate_overflow(count):
    player, combat, observed = prepare([Backstab() for _ in range(count)] + [Defend() for _ in range(8)], [SneckoEye()])
    first_decision(combat)
    assert len(observed.draws) == min(10, max(7, count))
    assert sum(c.innate for c in player.card_manager.get_pile("hand")) == min(10, count)
    assert all(observed.confused)


@pytest.mark.parametrize("lantern", [False, True])
def test_opening_void_energy_loss_is_not_erased_by_first_turn_refill(lantern):
    player, combat, _observed = prepare([Void()] + [Defend() for _ in range(4)], [Lantern()] if lantern else [])
    player.energy = 0  # leftover energy from the previous battle
    first_decision(combat)
    assert player.energy == (3 if lantern else 2)


def test_innate_and_bottled_same_card_is_drawn_once():
    card = Backstab()
    card.bottled = True
    bottle = BottledFlame()
    bottle.selected_card = card
    player, combat, observed = prepare([card] + [Defend() for _ in range(8)], [bottle])
    first_decision(combat)
    assert len(observed.draws) == 5
    assert observed.draws[0].innate
    assert sum(getattr(c, "origin_card") is card for c in observed.draws) == 1
    assert len(player.card_manager.get_pile("draw_pile")) == 4


def test_overflow_draw_follows_bonus_and_generated_card_actions():
    player, combat, observed = prepare([Backstab() for _ in range(7)] + [Defend() for _ in range(8)], [PureWater()])
    first_decision(combat)
    hand = player.card_manager.get_pile("hand")
    assert [type(c).__name__ for c in hand] == ["Backstab"] * 5 + ["Miracle"] + ["Backstab"] * 2
    assert len(observed.draws) == 7


def test_innate_overflow_draw_precedes_queued_autoplay_effect():
    from powers.definitions.mayhem import MayhemPower

    player, combat, observed = prepare([Backstab() for _ in range(7)] + [Defend() for _ in range(8)])
    combat._init_combat()
    game_state.drive_actions()
    player.add_power(MayhemPower(owner=player))
    hands_at_play = []

    class PlayObserver:
        priority = 0

        def handles(self, message):
            return isinstance(message, CardPlayedMessage)

        def handle(self, message):
            hands_at_play.append(len(player.card_manager.get_pile("hand")))
            return []

    game_state.message_bus.register(PlayObserver())
    combat._execute_player_start_phase()
    assert len(observed.draws) == 7
    assert hands_at_play == [7]


def test_second_turn_keeps_base_draw_without_repeating_opening_bonus():
    player, combat, observed = prepare([Defend() for _ in range(20)], [BagOfPreparation()])
    combat._init_combat()
    game_state.drive_actions()
    combat._execute_player_start_phase()
    assert len(observed.draws) == 7
    player.card_manager.get_pile("discard_pile").extend(player.card_manager.get_pile("hand"))
    player.card_manager.get_pile("hand").clear()
    combat._execute_player_start_phase()
    assert len(observed.draws) == 12
    assert len(player.card_manager.get_pile("hand")) == 5


@pytest.mark.parametrize("size", [0, 1, 12])
def test_initialization_uses_only_one_shuffle_domain_long(size):
    deck = [Defend() for _ in range(size)]
    player, combat, _observed = prepare(deck)
    before = copy(game_state.random_streams.export_state())
    combat._init_combat()
    after = game_state.random_streams.export_state()
    # Enemy selection may use ai; the remaining card-related streams are untouched.
    assert game_state.random_streams["shuffle"].counter == 1
    for domain in ("card", "card_random", "misc", "relic", "event"):
        assert before["streams"][domain] == after["streams"][domain]
    assert player.deck == deck


@pytest.mark.parametrize("reference", json.loads((Path(__file__).parent / "fixtures" / "opening_shuffle_reference.json").read_text()))
def test_opening_order_matches_original_rng_and_jdk_reference(reference):
    deck = [Defend() for _ in range(reference["size"])]
    for index, card in enumerate(deck):
        card.reference_index = index
        card._innate = index % 3 == 0
        card.bottled = index % 5 == 0
    player, combat, _observed = prepare(deck, seed=reference["seed"])
    combat._init_combat()
    actual = list(reversed(player.card_manager.get_pile("draw_pile")))
    assert [getattr(c, "reference_index") for c in actual] == reference["next_card_first"]
    assert game_state.random_streams["shuffle"].counter == 1
    assert game_state.random_streams["shuffle"].random_long() == reference["next_parent_long"]
