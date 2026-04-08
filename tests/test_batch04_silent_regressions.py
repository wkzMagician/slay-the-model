from typing import cast

from actions.card import DrawCardsAction, SetCostUntilEndOfTurnAction
from actions.card_choice import ChooseRetainCardAction, ChooseDiscardCardAction
from actions.combat import ApplyPowerAction
from cards.base import COST_X
from cards.colorless.shiv import Shiv
from cards.ironclad.strike import Strike
from cards.silent.after_image import AfterImage
from cards.silent.bullet_time import BulletTime
from cards.silent.bouncing_flask import BouncingFlask
from cards.silent.catalyst import Catalyst
from cards.silent.dagger_throw import DaggerThrow
from cards.silent.malaise import Malaise
from cards.silent.nightmare import Nightmare
from cards.silent.phantasmal_killer import PhantasmalKiller
from cards.silent.piercing_wail import PiercingWail
from cards.silent.storm_of_steel import StormOfSteel
from cards.silent.tools_of_the_trade import ToolsOfTheTrade
from cards.silent.well_laid_plans import WellLaidPlans
from enemies.act1.cultist import Cultist
from powers.definitions.phantasmal_killer import PhantasmalKillerPower
from powers.definitions.phantasmal_next_turn import PhantasmalNextTurnPower
from powers.definitions.tools_of_the_trade import ToolsOfTheTradePower
from powers.definitions.well_laid_plans import WellLaidPlansPower
from utils.types import RarityType, PilePosType
from tests.test_combat_utils import create_test_helper


def test_malaise_upgrade_retains_x_cost_and_exhausts_with_bonus_effect():
    helper = create_test_helper()
    player = helper.create_player(hp=70, max_hp=70, energy=2)
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])

    card = Malaise()
    card.upgrade()
    helper.add_card_to_hand(card)

    assert card._cost == COST_X
    assert card.exhaust is True
    assert card.rarity == RarityType.RARE
    assert helper.play_card(card, target=enemy)

    weak = enemy.get_power("Weak")
    strength = enemy.get_power("Strength")
    assert weak is not None and weak.amount == 3
    assert strength is not None and strength.amount == -3
    assert card in player.card_manager.get_pile("exhaust_pile")


def test_dagger_throw_uses_original_damage_value():
    helper = create_test_helper()
    player = helper.create_player(hp=70, max_hp=70, energy=3)
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])
    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
    helper.add_card_to_hand(Strike())
    card = DaggerThrow()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, target=enemy)
    assert enemy.hp == 31


def test_catalyst_and_nightmare_exhaust_with_correct_upgrade_cost():
    helper = create_test_helper()
    helper.create_player(hp=70, max_hp=70, energy=3)
    helper.start_combat([])

    catalyst = Catalyst()
    nightmare = Nightmare()
    nightmare.upgrade()

    assert catalyst.exhaust is True
    assert nightmare.exhaust is True
    assert nightmare.cost == 2


def test_bouncing_flask_uses_three_poison_per_hit():
    helper = create_test_helper()
    helper.create_player(hp=70, max_hp=70, energy=3)
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])

    card = BouncingFlask()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, target=enemy)
    poison = enemy.get_power("Poison")
    assert poison is not None
    assert poison.amount == 9


def test_storm_of_steel_upgraded_generates_upgraded_shivs_without_exhausting():
    helper = create_test_helper()
    player = helper.create_player(hp=70, max_hp=70, energy=3)
    helper.start_combat([])

    helper.add_card_to_hand(Strike())
    helper.add_card_to_hand(Strike())
    card = StormOfSteel()
    card.upgrade()
    helper.add_card_to_hand(card)

    assert card.exhaust is False
    assert card.cost == 1
    assert helper.play_card(card)

    shivs = [c for c in player.card_manager.get_pile("hand") if isinstance(c, Shiv)]
    assert len(shivs) == 2
    assert all(shiv.upgrade_level == 1 for shiv in shivs)
    assert all(shiv.damage == 6 for shiv in shivs)
    assert card in player.card_manager.get_pile("discard_pile")


def test_after_image_upgrade_grants_innate_without_reducing_cost():
    card = AfterImage()

    card.upgrade()

    assert card.innate is True
    assert card.cost == 1


def test_tools_of_the_trade_power_and_well_laid_plans_queue_amount_based_actions():
    helper = create_test_helper()
    player = helper.create_player(hp=70, max_hp=70, energy=3)
    helper.start_combat([])

    assert ToolsOfTheTrade().rarity == RarityType.RARE
    player.add_power(ToolsOfTheTradePower(amount=1, owner=player))
    player.add_power(ToolsOfTheTradePower(amount=1, owner=player))
    tools_power = player.get_power("Tools of the Trade")
    assert tools_power is not None
    assert tools_power.amount == 2
    tools_power.on_turn_start_post_draw()
    queued = helper.game_state.action_queue.queue
    draw_action = cast(DrawCardsAction, queued[0])
    discard_action = cast(ChooseDiscardCardAction, queued[1])
    assert isinstance(draw_action, DrawCardsAction)
    assert draw_action.count == 2
    assert isinstance(discard_action, ChooseDiscardCardAction)
    assert discard_action.amount == 2

    helper.game_state.action_queue.clear()
    player.add_power(WellLaidPlansPower(amount=1, owner=player))
    player.add_power(WellLaidPlansPower(amount=1, owner=player))
    retain_power = player.get_power("Well-Laid Plans")
    assert retain_power is not None
    assert retain_power.amount == 2
    retain_power.on_turn_end()
    queued = helper.game_state.action_queue.queue
    retain_action = cast(ChooseRetainCardAction, queued[0])
    assert isinstance(retain_action, ChooseRetainCardAction)
    assert retain_action.amount == 2


def test_card_rarity_fixes_for_piercing_wail_and_malaise():
    assert PiercingWail().rarity == RarityType.COMMON
    assert Malaise().rarity == RarityType.RARE


def test_bullet_time_applies_no_draw_before_zeroing_hand_costs():
    helper = create_test_helper()
    helper.create_player(hp=70, max_hp=70, energy=3)
    helper.start_combat([])
    helper.add_card_to_hand(Strike())
    helper.add_card_to_hand(Strike())
    card = BulletTime()

    card.on_play([])

    queued = helper.game_state.action_queue.queue
    no_draw_action = cast(ApplyPowerAction, queued[0])
    assert isinstance(no_draw_action, ApplyPowerAction)
    assert getattr(no_draw_action.power, "name", None) == "No Draw"
    assert all(isinstance(action, SetCostUntilEndOfTurnAction) for action in queued[1:])


def test_phantasmal_killer_powers_stack_as_turn_count():
    helper = create_test_helper()
    player = helper.create_player(hp=70, max_hp=70, energy=3)
    helper.start_combat([])

    card = PhantasmalKiller()
    assert card.cost == 1
    card.upgrade()
    assert card.cost == 0

    player.add_power(PhantasmalNextTurnPower(amount=1, duration=1, owner=player))
    player.add_power(PhantasmalNextTurnPower(amount=1, duration=1, owner=player))
    next_turn = player.get_power("Phantasmal Killer Next Turn")
    assert next_turn is not None
    assert next_turn.amount == 2

    next_turn.on_turn_start()
    helper.game_state.drive_actions()
    active = player.get_power("Phantasmal Killer")
    assert isinstance(active, PhantasmalKillerPower)

    active = cast(PhantasmalKillerPower, active)
    assert active.amount == 2
    active.on_turn_end()
    assert player.get_power("Phantasmal Killer") is not None
    remaining = cast(PhantasmalKillerPower, player.get_power("Phantasmal Killer"))
    assert remaining.amount == 1
    remaining.on_turn_end()
    assert player.get_power("Phantasmal Killer") is None
