"""CARD-002/016/017: a real card leaves hand before effects and closes once.

Cross-character hands are explicit prepared combat inputs. Randomness is only
fixed where indicated; card, potion, selection and effect implementations run.
"""

import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_status import UsePotionAction
from cards.colorless.shiv import Shiv
from cards.defect.reboot import Reboot
from cards.defect.skim import Skim
from cards.ironclad.defend import Defend
from cards.ironclad.havoc import Havoc
from cards.ironclad.offering import Offering
from cards.ironclad.strike import Strike
from cards.silent.acrobatics import Acrobatics
from cards.silent.backflip import Backflip
from cards.silent.blade_dance import BladeDance
from cards.silent.calculated_gamble import CalculatedGamble
from cards.silent.dagger_spray import DaggerSpray
from cards.silent.storm_of_steel import StormOfSteel
from enemies.act1.cultist import Cultist
from engine.messages import CardDiscardedMessage, CardDrawnMessage, CardExhaustedMessage, CardPlayedMessage
from potions.global_potions import DistilledChaos
from powers.definitions.corruption import CorruptionPower
from powers.definitions.dark_embrace import DarkEmbracePower
from powers.definitions.feel_no_pain import FeelNoPainPower
from relics.global_relics.shop import StrangeSpoonShop
from tests.test_combat_utils import create_test_helper


def prepare(monkeypatch, draw_count=8):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=5)
    player.base_draw_count = 0
    enemy = Cultist()
    enemy._max_hp = 1000
    enemy.hp = 1000
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    player.card_manager.piles["draw_pile"] = [Defend() for _ in range(draw_count)]
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, combat, messages


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


def events(messages, kind):
    return [message for message in messages if isinstance(message, kind)]


@pytest.mark.parametrize("card_type,hand_size,drawn", [(Backflip, 1, 2), (Backflip, 9, 2), (Backflip, 10, 1), (Skim, 10, 1)])
def test_draw_card_releases_its_hand_slot_before_drawing(card_type, hand_size, drawn, monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    player.card_manager.piles["hand"] = [Defend() for _ in range(hand_size - 1)]
    card = card_type()
    assert play(helper, card) is None
    assert len(events(messages, CardDrawnMessage)) == drawn
    assert len(player.card_manager.piles["hand"]) == hand_size - 1 + drawn
    assert player.card_manager.get_card_location(card) == "discard_pile"
    assert all(message.card is not card for message in events(messages, CardDrawnMessage))


def test_upgraded_calculated_gamble_discards_other_card_and_draws_one(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    other = Defend()
    helper.add_card_to_hand(other)
    card = CalculatedGamble()
    card.upgrade()
    assert play(helper, card) is None
    assert [message.card for message in events(messages, CardDiscardedMessage)] == [other]
    assert len(events(messages, CardDrawnMessage)) == 1
    assert len(player.card_manager.piles["hand"]) == 1
    assert combat.combat_state.discarded_cards_this_turn == 1
    assert player.card_manager.get_card_location(card) == "discard_pile"


def test_storm_of_steel_does_not_discard_itself_or_create_extra_shiv(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch)
    other = Defend()
    helper.add_card_to_hand(other)
    card = StormOfSteel()
    assert play(helper, card) is None
    assert [message.card for message in events(messages, CardDiscardedMessage)] == [other]
    assert combat.combat_state.discarded_cards_this_turn == 1
    assert len(player.card_manager.piles["hand"]) == 1
    assert isinstance(player.card_manager.piles["hand"][0], Shiv)
    assert player.card_manager.get_card_location(card) == "discard_pile"


def test_empty_acrobatics_does_not_select_or_discard_itself(monkeypatch):
    helper, player, _, combat, messages = prepare(monkeypatch, draw_count=0)
    card = Acrobatics()
    assert play(helper, card) is None
    assert not events(messages, CardDrawnMessage)
    assert not events(messages, CardDiscardedMessage)
    assert combat.combat_state.discarded_cards_this_turn == 0
    assert player.card_manager.piles["hand"] == []
    assert player.card_manager.piles["discard_pile"] == [card]


def test_reboot_does_not_shuffle_or_redraw_its_in_use_self(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch, draw_count=0)
    card = Reboot()
    assert play(helper, card) is None
    assert not events(messages, CardDrawnMessage)
    assert player.card_manager.piles["hand"] == []
    assert player.card_manager.piles["exhaust_pile"] == [card]


@pytest.mark.parametrize("hand_size,hand_shivs,discard_shivs", [(8, 3, 0), (9, 2, 1), (10, 1, 2)])
def test_blade_dance_capacity_uses_released_slot(hand_size, hand_shivs, discard_shivs, monkeypatch):
    helper, player, _, _, _ = prepare(monkeypatch)
    player.card_manager.piles["hand"] = [Defend() for _ in range(hand_size - 1)]
    assert play(helper, BladeDance()) is None
    assert sum(isinstance(card, Shiv) for card in player.card_manager.piles["hand"]) == hand_shivs
    assert sum(isinstance(card, Shiv) for card in player.card_manager.piles["discard_pile"]) == discard_shivs
    assert len(player.card_manager.piles["hand"]) == 10


@pytest.mark.parametrize("pain,embrace,block,drawn", [(False, False, 0, 0), (True, False, 3, 0), (False, True, 0, 1), (True, True, 3, 1)])
def test_shiv_finalizes_exhaust_once_with_passive_benefits(pain, embrace, block, drawn, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    if pain:
        player.add_power(FeelNoPainPower(amount=3, owner=player))
    if embrace:
        player.add_power(DarkEmbracePower(amount=1, owner=player))
    card = Shiv()
    assert play(helper, card) is None
    assert enemy.hp == 996
    assert player.block == block
    assert len(events(messages, CardDrawnMessage)) == drawn
    assert [message.card for message in events(messages, CardExhaustedMessage)] == [card]
    assert player.card_manager.piles["exhaust_pile"] == [card]


def test_offering_draws_its_three_cards_and_one_exhaust_bonus(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    player.add_power(FeelNoPainPower(amount=3, owner=player))
    player.add_power(DarkEmbracePower(amount=1, owner=player))
    card = Offering()
    assert play(helper, card) is None
    assert player.hp == 94
    assert player.energy == 7
    assert player.block == 3
    assert len(events(messages, CardDrawnMessage)) == 4
    assert len(player.card_manager.piles["hand"]) == 4
    assert [message.card for message in events(messages, CardExhaustedMessage)] == [card]


@pytest.mark.parametrize("roll,prevented", [(0.0, True), (0.9, False)])
def test_strange_spoon_decides_single_final_destination_and_exhaust_benefits(roll, prevented, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    player.relics.append(StrangeSpoonShop())
    player.add_power(FeelNoPainPower(amount=3, owner=player))
    player.add_power(DarkEmbracePower(amount=1, owner=player))
    # Prepared RNG input chooses the real relic's two branches; no hook replaced.
    monkeypatch.setattr("random.random", lambda: roll)
    card = Shiv()
    assert play(helper, card) is None
    assert enemy.hp == 996
    assert player.block == (0 if prevented else 3)
    assert len(events(messages, CardDrawnMessage)) == (0 if prevented else 1)
    assert [message.card for message in events(messages, CardExhaustedMessage)] == ([] if prevented else [card])
    assert player.card_manager.get_card_location(card) == ("discard_pile" if prevented else "exhaust_pile")


def test_real_blade_dance_generated_shiv_exhausts_only_once(monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch)
    player.add_power(FeelNoPainPower(amount=3, owner=player))
    assert play(helper, BladeDance()) is None
    shiv = next(card for card in player.card_manager.piles["hand"] if isinstance(card, Shiv))
    helper.game_state.add_action(PlayCardAction(shiv))
    assert helper.game_state.drive_actions() is None
    assert enemy.hp == 996
    assert player.block == 3
    assert [message.card for message in events(messages, CardExhaustedMessage)] == [shiv]
    assert sum(isinstance(card, Shiv) for card in player.card_manager.piles["hand"]) == 2


def test_corruption_forced_exhaust_control_is_still_single(monkeypatch):
    helper, player, _, _, messages = prepare(monkeypatch)
    player.add_power(CorruptionPower(owner=player))
    player.add_power(FeelNoPainPower(amount=3, owner=player))
    card = Defend()
    assert play(helper, card) is None
    assert player.block == 8
    assert [message.card for message in events(messages, CardExhaustedMessage)] == [card]


@pytest.mark.parametrize("bottom_type,top_type,damage,block", [(Strike, Defend, 0, 5), (Defend, Strike, 6, 0)])
def test_havoc_uses_actual_top_card_and_exhausts_only_it(bottom_type, top_type, damage, block, monkeypatch):
    helper, player, enemy, _, messages = prepare(monkeypatch, draw_count=0)
    bottom, top = bottom_type(), top_type()
    player.card_manager.piles["draw_pile"] = [bottom, top]
    assert play(helper, Havoc()) is None
    assert enemy.hp == 1000 - damage
    assert player.block == block
    assert player.card_manager.piles["draw_pile"] == [bottom]
    assert player.card_manager.piles["exhaust_pile"] == [top]
    assert [message.card for message in events(messages, CardPlayedMessage)][1] is top


def test_chaos_preselected_dead_target_does_not_retarget_second_attack(monkeypatch):
    helper, player, first, combat, messages = prepare(monkeypatch, draw_count=0)
    first.hp = 6
    survivor = Cultist()
    survivor._max_hp = 100
    survivor.hp = 100
    combat.enemies.append(survivor)
    attack1, attack2, defense = Strike(), Strike(), Defend()
    player.card_manager.piles["draw_pile"] = [defense, attack2, attack1]
    # All three original PlayTopCard producers preselect the first living enemy.
    # This fixes RNG only and delegates the real potion and card implementations.
    monkeypatch.setattr("random.choice", lambda choices: choices[0])
    item = DistilledChaos()
    player.potions.append(item)
    helper.game_state.add_action(UsePotionAction(item, target=player))
    assert helper.game_state.drive_actions() is None
    assert first.hp == 0
    assert survivor.hp == 100
    assert player.block == 5  # SELF must ignore the obsolete enemy binding.
    assert [message.card for message in events(messages, CardPlayedMessage)] == [attack1, defense]
    assert player.card_manager.get_card_location(attack2) == "discard_pile"


def test_chaos_enemy_all_ignores_single_preselected_target(monkeypatch):
    helper, player, first, combat, messages = prepare(monkeypatch, draw_count=0)
    survivor = Cultist()
    survivor._max_hp = 100
    survivor.hp = 100
    combat.enemies.append(survivor)
    card = DaggerSpray()
    player.card_manager.piles["draw_pile"] = [card]
    # Preselect one enemy through the real producer; AoE must still hit both.
    monkeypatch.setattr("random.choice", lambda choices: choices[0])
    item = DistilledChaos()
    player.potions.append(item)
    helper.game_state.add_action(UsePotionAction(item, target=player))
    assert helper.game_state.drive_actions() is None
    assert first.hp == 992
    assert survivor.hp == 92
    assert [message.card for message in events(messages, CardPlayedMessage)] == [card]
    assert player.card_manager.get_card_location(card) == "discard_pile"
