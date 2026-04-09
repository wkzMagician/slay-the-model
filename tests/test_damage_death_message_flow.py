from actions.combat import DealDamageAction, LoseHPAction
from cards.ironclad.feed import Feed
from cards.ironclad.blood_for_blood import BloodForBlood
from cards.ironclad.strike import Strike
from cards.silent.masterful_stab import MasterfulStab
from enemies.act1.cultist import Cultist
from enemies.act1.fungi_beast import FungiBeast
from engine.messages import (
    AnyHpLostMessage,
    DamageDealtMessage,
    DirectHpLossMessage,
    FatalDamageMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
)
from relics.character.defect import EmotionChip
from relics.character.ironclad import RedSkull, RunicCube
from relics.global_relics.common import CentennialPuzzle
from relics.global_relics.uncommon import SelfFormingClay
from orbs.lightning import LightningOrb
from tests.test_combat_utils import create_test_helper
from utils.types import DamageType, PilePosType


def test_damage_actions_import_from_split_modules():
    from actions.combat import DealDamageAction as CombatDealDamageAction
    from actions.combat import HealAction as CombatHealAction
    from actions.combat_damage import DealDamageAction as SplitDealDamageAction
    from actions.combat_damage import HealAction as SplitHealAction

    assert CombatDealDamageAction is SplitDealDamageAction
    assert CombatHealAction is SplitHealAction


def _capture_published_message_types(game_state, monkeypatch):
    original_publish = game_state.publish_message
    published = []

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", wrapped)
    return published


def test_deal_damage_action_publishes_damage_dealt_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    red_skull = RedSkull()
    player.relics = [red_skull]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=25, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert "DamageDealtMessage" in published
    assert player.strength == 3


def test_deal_damage_action_publishes_creature_died_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(FungiBeast, hp=1)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=5, target=enemy, source=player).execute()
    helper.game_state.drive_actions()

    assert "DamageDealtMessage" in published
    assert "CreatureDiedMessage" in published
    assert "FatalDamageMessage" in published
    assert player.has_power("Vulnerable")


def test_deal_damage_action_preserves_card_on_fatal(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=10)
    helper.start_combat([enemy])
    card = Feed()
    initial_max_hp = player.max_hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=10, target=enemy, source=player, card=card, damage_type="attack").execute()
    helper.game_state.drive_actions()

    assert "DamageDealtMessage" in published
    assert "CreatureDiedMessage" in published
    assert "FatalDamageMessage" in published
    assert player.max_hp == initial_max_hp + 3


def test_damage_type_exposes_explicit_semantics():
    assert DamageType.PHYSICAL.value == "physical"
    assert DamageType.MAGICAL.value == "magical"
    assert DamageType.HP_LOSS.value == "hp_loss"


def test_physical_damage_publishes_explicit_attack_and_hp_loss_messages(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=7, target=player, source=enemy, damage_type=DamageType.PHYSICAL).execute()
    helper.game_state.drive_actions()

    assert "DamageDealtMessage" in published
    assert "PhysicalAttackTakenMessage" in published
    assert "PhysicalAttackDealtMessage" in published
    assert "AnyHpLostMessage" in published


def test_hp_loss_publishes_direct_and_any_hp_loss_messages(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    LoseHPAction(amount=4, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert "HpLostMessage" in published
    assert "DirectHpLossMessage" in published
    assert "AnyHpLostMessage" in published


def test_runic_cube_draws_on_any_hp_lost_from_physical_damage():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    player.relics.append(RunicCube())
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)

    DealDamageAction(damage=6, target=player, source=enemy, damage_type=DamageType.PHYSICAL).execute()
    helper.game_state.drive_actions()

    assert player.hp == 44
    assert len(player.card_manager.get_pile("hand")) == 1


def test_blood_for_blood_cost_changes_on_any_hp_lost():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    card = BloodForBlood()
    helper.add_card_to_hand(card)

    DealDamageAction(damage=6, target=player, source=enemy, damage_type=DamageType.PHYSICAL).execute()
    helper.game_state.drive_actions()

    assert card.cost == 3


def test_masterful_stab_cost_changes_on_any_hp_lost():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    card = MasterfulStab()
    helper.add_card_to_hand(card)

    LoseHPAction(amount=3, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert card.cost == 1


def test_red_skull_activates_after_direct_hp_loss():
    helper = create_test_helper()
    player = helper.create_player(hp=45, max_hp=100, energy=3)
    player.relics.append(RedSkull())
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    LoseHPAction(amount=5, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert player.hp == 40
    assert player.strength == 3


def test_centennial_puzzle_triggers_on_direct_hp_loss():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    player.relics.append(CentennialPuzzle())
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)

    LoseHPAction(amount=3, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert len(player.card_manager.get_pile("hand")) == 3


def test_self_forming_clay_tracks_direct_hp_loss():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    player.relics.append(SelfFormingClay())
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    LoseHPAction(amount=3, target=player, source=enemy).execute()
    helper.game_state.drive_actions()
    combat = helper.game_state.current_combat
    assert combat is not None
    combat._start_player_turn()
    helper.game_state.drive_actions()

    assert player.block == 3


def test_emotion_chip_tracks_any_hp_loss():
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    player.relics.append(EmotionChip())
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.orb_manager.add_orb(LightningOrb())

    LoseHPAction(amount=3, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    player.block = 0
    combat = helper.game_state.current_combat
    assert combat is not None
    combat._start_player_turn()
    helper.game_state.drive_actions()

    assert enemy.hp < 30

