"""PWR-039: phase-transition ClearCardQueue differs from end-turn cleanup.

Original PlayTopCardAction unlimbos before NewQueueCardAction. Clearing those
requests neither discards nor exhausts the unplayed cards (ExhaustCardEffect is
only visual). Tests use real potion/card producers with prepared combat piles.
"""

import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_status import UsePotionAction
from cards.ironclad.defend import Defend
from cards.ironclad.havoc import Havoc
from cards.ironclad.impervious import Impervious
from cards.ironclad.pummel import Pummel
from cards.ironclad.strike import Strike
from enemies.act3.awakened_one import AwakenedOne
from engine.messages import CardDiscardedMessage, CardExhaustedMessage, CardPlayedMessage
from potions.global_potions import DistilledChaos
from powers.definitions.double_tap import DoubleTapPower
from relics.global_relics.boss import SacredBark
from tests.test_combat_utils import create_test_helper


def prepare(monkeypatch, ascension=0, hp=1):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=6)
    player.base_draw_count = 0
    helper.game_state.ascension = ascension
    enemy = AwakenedOne()
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    enemy.hp = hp
    messages = []
    publish_original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return publish_original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, combat, messages


def chaos(helper, player):
    potion = DistilledChaos()
    player.potions.append(potion)
    helper.game_state.add_action(UsePotionAction(potion, target=player))
    assert helper.game_state.drive_actions() is None


def played(messages):
    return [message.card for message in messages if isinstance(message, CardPlayedMessage)]


@pytest.mark.parametrize("ascension", [0, 19])
@pytest.mark.parametrize("pending_type", [Defend, Impervious, Havoc])
def test_chaos_phase_transition_removes_pending_without_play_or_card_cleanup(
    ascension, pending_type, monkeypatch,
):
    helper, player, enemy, combat, messages = prepare(monkeypatch, ascension)
    first, second, third, untouched = Strike(), pending_type(), Defend(), Defend()
    player.card_manager.piles["draw_pile"] = [untouched, third, second, first]
    chaos(helper, player)
    assert played(messages) == [first]
    assert enemy.half_dead and not enemy.is_dead()
    assert player.block == 0 and player.energy == 6
    assert combat.combat_state.turn_cards_played == 1
    assert player.card_manager.get_card_location(first) == "discard_pile"
    assert player.card_manager.get_card_location(second) is None
    assert player.card_manager.get_card_location(third) is None
    assert player.card_manager.get_card_location(untouched) == "draw_pile"
    assert not any(isinstance(message, CardExhaustedMessage) for message in messages)
    assert not any(isinstance(message, CardDiscardedMessage) and message.card in (second, third)
                   for message in messages)
    assert not helper.game_state.pending_card_plays
    assert not helper.game_state.active_card_plays
    assert not player.card_manager.piles.get("limbo")

    # ClearCardQueueAction does not end the player turn or forbid later cards.
    manual = Defend()
    helper.add_card_to_hand(manual)
    helper.game_state.add_action(PlayCardAction(manual))
    assert helper.game_state.drive_actions() is None
    assert played(messages) == [first, manual]
    assert player.block == 5 and player.energy == 5
    assert combat.combat_state.current_phase == "player_action"


@pytest.mark.parametrize("ascension", [0, 19])
def test_phase_clear_preserves_current_exhausting_attack_cleanup(ascension, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch, ascension)
    first, second, third = Pummel(), Impervious(), Defend()
    player.card_manager.piles["draw_pile"] = [third, second, first]
    chaos(helper, player)
    assert played(messages) == [first]
    assert enemy.half_dead
    assert player.block == 0
    assert player.card_manager.get_card_location(first) == "exhaust_pile"
    assert player.card_manager.get_card_location(second) is None
    assert player.card_manager.get_card_location(third) is None
    assert [message.card for message in messages if isinstance(message, CardExhaustedMessage)] == [first]


def test_phase_clear_cancels_replay_and_chaos_originals_together(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    player.add_power(DoubleTapPower(amount=1, owner=player))
    first, second, third = Strike(), Defend(), Defend()
    player.card_manager.piles["draw_pile"] = [third, second, first]
    chaos(helper, player)
    assert played(messages) == [first]
    assert combat.combat_state.turn_cards_played == 1
    assert player.block == 0
    assert player.card_manager.piles["discard_pile"] == [first]
    assert not player.card_manager.piles.get("exhaust_pile")
    assert not player.card_manager.piles.get("limbo")
    assert not helper.game_state.pending_card_plays


def test_sacred_bark_phase_clear_removes_all_five_remaining_requests(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    player.relics.append(SacredBark())
    first = Strike()
    pending = [Defend() for _ in range(5)]
    player.card_manager.piles["draw_pile"] = pending + [first]
    chaos(helper, player)
    assert played(messages) == [first]
    assert player.block == 0
    assert all(player.card_manager.get_card_location(card) is None for card in pending)
    assert player.card_manager.piles["discard_pile"] == [first]


def test_nonlethal_chaos_retains_all_three_normal_plays(monkeypatch):
    helper, player, enemy, combat, messages = prepare(monkeypatch, hp=100)
    first, second, third = Strike(), Defend(), Defend()
    player.card_manager.piles["draw_pile"] = [third, second, first]
    chaos(helper, player)
    assert played(messages) == [first, second, third]
    assert enemy.hp == 94 and not enemy.half_dead
    assert player.block == 10 and combat.combat_state.turn_cards_played == 3
    assert player.card_manager.piles["discard_pile"] == [first, second, third]


def test_later_chaos_can_play_skills_while_awakened_waits_for_rebirth(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    first = Strike()
    helper.add_card_to_hand(first)
    helper.game_state.add_action(PlayCardAction(first))
    assert helper.game_state.drive_actions() is None
    assert enemy.half_dead
    defense = [Defend() for _ in range(3)]
    player.card_manager.piles["draw_pile"] = defense.copy()
    chaos(helper, player)
    assert played(messages) == [first, *reversed(defense)]
    assert player.block == 15
    assert all(player.card_manager.get_card_location(card) == "discard_pile" for card in defense)
