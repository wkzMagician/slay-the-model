from cards.ironclad.battle_trance import BattleTrance
from cards.ironclad.barricade import Barricade
from cards.ironclad.blood_for_blood import BloodForBlood
from cards.ironclad.defend import Defend
from cards.ironclad.exhume import Exhume
from cards.ironclad.feed import Feed
from cards.ironclad.fiend_fire import FiendFire
from cards.ironclad.reaper import Reaper
from cards.ironclad.strike import Strike
from cards.ironclad.whirlwind import Whirlwind
from cards.colorless.wound import Wound
from enemies.act1.cultist import Cultist
from powers.definitions.corruption import CorruptionPower
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


def test_feed_and_reaper_are_exhaust_cards():
    assert Feed().exhaust is True
    assert Reaper().exhaust is True


def test_battle_trance_and_entrench_costs_match_batch03_spec():
    from cards.ironclad.entrench import Entrench

    battle_trance = BattleTrance()
    entrench = Entrench()
    entrench.upgrade()

    assert battle_trance.cost == 0
    assert Entrench().cost == 2
    assert entrench.cost == 1


def test_exhume_cannot_return_exhume_from_exhaust_pile():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    first_exhume = Exhume()
    strike = Strike()
    player.card_manager.piles["exhaust_pile"].append(first_exhume)
    player.card_manager.piles["exhaust_pile"].append(strike)

    second_exhume = Exhume()
    helper.add_card_to_hand(second_exhume)
    assert helper.play_card(second_exhume, target=enemy)

    hand = player.card_manager.get_pile("hand")
    assert strike in hand
    assert first_exhume not in hand


def test_blood_for_blood_upgrade_preserves_and_improves_reduced_cost():
    card = BloodForBlood()
    card.on_any_hp_lost(1)
    card.on_any_hp_lost(1)

    assert card.cost == 2
    card.upgrade()
    assert card.cost == 1


def test_fiend_fire_exhausts_other_hand_cards_and_itself():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    enemy = helper.create_enemy(Cultist, hp=80)
    helper.start_combat([enemy])

    first = Strike()
    second = Strike()
    helper.add_card_to_hand(first)
    helper.add_card_to_hand(second)
    card = FiendFire()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, target=enemy)

    exhaust_pile = player.card_manager.get_pile("exhaust_pile")
    assert card in exhaust_pile
    assert first in exhaust_pile
    assert second in exhaust_pile


def test_blood_for_blood_cost_reduces_after_hp_loss_in_combat():
    helper = create_test_helper()
    player = helper.create_player(hp=40, max_hp=40, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    card = BloodForBlood()
    helper.add_card_to_hand(card)

    from actions.combat_damage import LoseHPAction

    LoseHPAction(amount=3, target=player).execute()
    helper.game_state.drive_actions()

    assert card.cost == 3


def test_corruption_makes_drawn_skills_free_and_exhaust_on_play():
    helper = create_test_helper()
    player = helper.create_player(hp=40, max_hp=40, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.add_power(CorruptionPower(owner=player))

    defend = Defend()
    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.add_to_pile(defend, "draw_pile", PilePosType.TOP)

    from actions.card import DrawCardsAction

    DrawCardsAction(count=1).execute()
    helper.game_state.drive_actions()

    from actions.combat import PlayCardAction

    assert defend.cost == 0
    PlayCardAction(card=defend).execute()
    helper.game_state.drive_actions()
    assert defend in player.card_manager.get_pile("exhaust_pile")


def test_cost_setter_does_not_overwrite_x_or_unplayable_cards():
    whirlwind = Whirlwind()
    wound = Wound()

    whirlwind.cost = 2
    wound.cost = 1

    assert whirlwind._cost == -1
    assert wound._cost == -2


def test_upgrade_description_replaces_base_description_when_present():
    card = Barricade()
    base_description = card.description.resolve()

    card.upgrade()
    upgraded_description = card.description.resolve()

    assert upgraded_description != base_description
