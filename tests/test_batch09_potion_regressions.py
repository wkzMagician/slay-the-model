from typing import cast

from unittest.mock import patch

from actions.reward import AddRandomPotionAction
from actions.combat import UsePotionAction, UsePotionBHAction
from actions.display import InputRequestAction
from actions.watcher import ChangeStanceAction
from cards.ironclad.strike import Strike
from enemies.act1.slime_boss import SlimeBoss
from enemies.act1.cultist import Cultist
from engine.messages import PlayerTurnEndedMessage
from potions.global_potions import (
    BlessingOfTheForge,
    DuplicationPotion,
    EntropicBrew,
    FearPotion,
    FirePotion,
    LiquidMemories,
    SmokeBomb,
)
from relics.global_relics.boss import SacredBark
from relics.global_relics.common import PotionBelt
from potions.watcher import Ambrosia, StancePotion
from powers.definitions.intangible import IntangiblePower
from relics.character.watcher import VioletLotus
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import CombatType, RarityType, StatusType
from utils.random import get_random_relic


def _first_input_request(helper):
    for action in helper.game_state.action_queue.queue:
        if isinstance(action, InputRequestAction):
            return action
    raise AssertionError("expected an InputRequestAction in the queue")


def test_enemy_target_potions_do_not_prebind_player_target():
    helper = create_test_helper()
    player = helper.create_player()
    enemy_a = helper.create_enemy(Cultist, hp=30)
    enemy_b = helper.create_enemy(Cultist, hp=30)
    combat = helper.start_combat([enemy_a, enemy_b])
    potion = FearPotion()
    player.potions.append(potion)

    combat._build_player_action()

    request = cast(InputRequestAction, _first_input_request(helper))
    potion_action = next(
        action
        for option in request.options
        for action in option.actions
        if isinstance(action, UsePotionAction) and action.potion is potion
    )

    assert potion_action.target is None


def test_stance_potion_routes_choices_through_change_stance_action():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    potion = StancePotion()

    UsePotionBHAction(potion=potion, targets=[player]).execute()

    request = cast(InputRequestAction, _first_input_request(helper))
    assert all(isinstance(option.actions[0], ChangeStanceAction) for option in request.options)


def test_ambrosia_queues_change_stance_action_instead_of_setting_status_directly():
    helper = create_test_helper()
    player = helper.create_player(energy=3, max_energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    player.relics.append(VioletLotus())
    player.status_manager.status = StatusType.CALM
    potion = Ambrosia()

    potion.on_use([player])

    assert player.status_manager.status == StatusType.CALM
    next_action = cast(ChangeStanceAction, helper.game_state.action_queue.peek_next())
    assert isinstance(next_action, ChangeStanceAction)
    assert next_action.status == StatusType.DIVINITY


def test_fire_potion_respects_intangible_on_target():
    helper = create_test_helper()
    helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])
    enemy.add_power(IntangiblePower(duration=1, owner=enemy))
    potion = FirePotion()

    UsePotionBHAction(potion=potion, targets=[enemy]).execute()
    helper.game_state.drive_actions()

    assert enemy.hp == 39


def test_duplication_potion_expires_at_end_of_round_without_card_play():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    potion = DuplicationPotion()

    UsePotionBHAction(potion=potion, targets=[player]).execute()
    helper.game_state.drive_actions()
    assert player.get_power("Duplication") is not None

    helper.game_state.publish_message(
        PlayerTurnEndedMessage(owner=player, enemies=[], hand_cards=[]),
    )
    helper.game_state.drive_actions()

    assert player.get_power("Duplication") is None


def test_smoke_bomb_cannot_be_used_in_boss_combat():
    helper = create_test_helper()
    player = helper.create_player()
    boss = SlimeBoss()
    helper.start_combat([boss])
    assert helper.game_state.current_combat is not None
    helper.game_state.current_combat.combat_type = CombatType.BOSS
    potion = SmokeBomb()
    player.potions.append(potion)

    UsePotionBHAction(potion=potion, targets=[player]).execute()
    helper.game_state.drive_actions()

    assert potion in player.potions
    assert helper.game_state.terminal_state is not GameTerminalState.COMBAT_ESCAPE


def test_blessing_of_the_forge_is_common():
    assert BlessingOfTheForge.rarity == RarityType.COMMON


def test_entropic_brew_refills_all_slots_after_consumption():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    player.potions.clear()
    player.potions.append(EntropicBrew())

    UsePotionBHAction(potion=player.potions[0], targets=[player]).execute()
    helper.game_state.drive_actions()

    assert len(player.potions) == player.potion_limit


def test_sacred_bark_liquid_memories_allows_selecting_two_cards():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    player.relics.append(SacredBark())
    strike_a = Strike()
    strike_b = Strike()
    player.card_manager.piles["discard_pile"] = [strike_a, strike_b]
    potion = LiquidMemories()

    potion.on_use([player])

    request = cast(InputRequestAction, _first_input_request(helper))
    assert request.max_select == 2


def test_potion_belt_does_not_spawn_after_floor_48():
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.current_floor = 49

    with patch("utils.random.list_registered", return_value=["PotionBelt"]), patch(
        "utils.random.get_registered", return_value=PotionBelt
    ):
        relic = get_random_relic(rarities=[RarityType.COMMON])

    assert relic is None
