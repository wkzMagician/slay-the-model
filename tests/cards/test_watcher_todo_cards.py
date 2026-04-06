from cards.colorless.miracle import Miracle
from cards.ironclad.strike import Strike as IroncladStrike
from cards.watcher import (
    Brilliance,
    FearNoEvil,
    ForeignInfluence,
    Indignation,
    Meditate,
    Omniscience,
    SimmeringFury,
    SpiritShield,
    Swivel,
    Tantrum,
    Wallop,
)
from enemies.act1.cultist import Cultist
from powers.definitions.collect import CollectPower
from relics.character.watcher import Melange
from tests.test_combat_utils import create_test_helper
from utils.types import StatusType


def test_wallop_gains_block_equal_to_actual_damage_dealt():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    enemy.block = 7
    helper.start_combat([enemy])

    card = Wallop()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy) is True
    assert player.block == 2


def test_fear_no_evil_enters_calm_if_target_intends_attack():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    enemy.current_intention = enemy.intentions["attack"]

    card = FearNoEvil()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy) is True
    assert player.status_manager.status == StatusType.CALM


def test_foreign_influence_only_upgraded_card_is_zero_cost_this_turn():
    base_card = ForeignInfluence()
    upgraded_card = ForeignInfluence()
    upgraded_card.upgrade()

    assert base_card.upgrade_level == 0
    assert upgraded_card.upgrade_level == 1
    assert "0 this turn" in upgraded_card.text_description

    helper = create_test_helper()
    helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    helper.add_card_to_hand(base_card)
    helper.add_card_to_hand(upgraded_card)

    assert helper.play_card(base_card) is True
    assert helper.play_card(upgraded_card) is True

    hand = helper.game_state.player.card_manager.get_pile("hand")
    zero_cost_count = sum(1 for card in hand if getattr(card, "cost_until_end_of_turn", None) == 0)
    assert zero_cost_count == 1


def test_tantrum_shuffles_itself_into_draw_pile_after_play():
    helper = create_test_helper()
    helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])

    card = Tantrum()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy) is True
    assert card in helper.game_state.player.card_manager.get_pile("draw_pile")


def test_brilliance_damage_scales_with_mantra():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    player.add_power(CollectPower(owner=player))
    player.add_power(type("TestMantra", (), {"name": "Mantra", "amount": 5})())

    card = Brilliance()

    assert card.damage == 17


def test_spirit_shield_block_scales_with_cards_in_hand():
    helper = create_test_helper()
    helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])

    card = SpiritShield()
    helper.add_card_to_hand(card)
    helper.add_card_to_hand(IroncladStrike())
    helper.add_card_to_hand(IroncladStrike())

    assert card.block == 9


def test_omniscience_plays_selected_card_twice_and_exhausts_it():
    helper = create_test_helper()
    player = helper.create_player(energy=10)
    enemy = helper.create_enemy(Cultist, hp=50)
    helper.start_combat([enemy])

    omniscience = Omniscience()
    strike = IroncladStrike()
    helper.add_card_to_hand(omniscience)
    helper.add_card_to_hand(strike)

    assert helper.play_card(omniscience) is True
    assert enemy.hp == 38
    assert strike in player.card_manager.get_pile("exhaust_pile")


def test_collect_power_adds_base_miracle_at_turn_start():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    player.add_power(CollectPower(duration=1, owner=player))

    combat = helper.game_state.current_combat
    assert combat is not None
    combat._start_player_turn()
    helper.game_state.drive_actions()

    miracles = [card for card in player.card_manager.get_pile("hand") if isinstance(card, Miracle)]
    assert len(miracles) == 1
    assert miracles[0].upgrade_level == 1


def test_swivel_only_makes_the_next_attack_free_for_the_turn():
    helper = create_test_helper()
    player = helper.create_player(energy=10)
    enemy = helper.create_enemy(Cultist, hp=50)
    helper.start_combat([enemy])

    swivel = Swivel()
    first_attack = IroncladStrike()
    second_attack = IroncladStrike()
    helper.add_card_to_hand(swivel)
    helper.add_card_to_hand(first_attack)
    helper.add_card_to_hand(second_attack)

    assert helper.play_card(swivel) is True
    assert first_attack.cost == 0
    assert second_attack.cost == 0

    assert helper.play_card(first_attack, enemy) is True
    assert second_attack.cost == 1


def test_indignation_enters_wrath_when_not_already_in_wrath():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    card = Indignation()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy) is True
    assert player.status_manager.status == StatusType.WRATH


def test_indignation_applies_vulnerable_to_all_enemies_when_already_in_wrath():
    helper = create_test_helper()
    player = helper.create_player()
    enemy_one = helper.create_enemy(Cultist, hp=30)
    enemy_two = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy_one, enemy_two])
    player.status_manager.status = StatusType.WRATH

    card = Indignation()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy_one) is True
    assert enemy_one.get_power("Vulnerable") is not None
    assert enemy_two.get_power("Vulnerable") is not None


def test_meditate_returns_card_enters_calm_and_ends_turn():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    combat = helper.start_combat([enemy])
    card = Meditate()
    strike = IroncladStrike()
    helper.add_card_to_discard_pile(strike)
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True
    assert strike in player.card_manager.get_pile("hand")
    assert player.status_manager.status == StatusType.CALM
    assert combat.combat_state.current_phase == "player_end"


def test_simmering_fury_enters_wrath_and_draws_next_turn_not_now():
    helper = create_test_helper()
    player = helper.create_player()
    enemy = helper.create_enemy(Cultist, hp=30)
    combat = helper.start_combat([enemy])
    player.base_draw_count = 0
    helper.add_card_to_draw_pile(IroncladStrike())
    helper.add_card_to_draw_pile(IroncladStrike())
    card = SimmeringFury()
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True
    assert player.status_manager.status == StatusType.NEUTRAL
    assert len(player.card_manager.get_pile("hand")) == 0

    combat._start_player_turn()
    helper.game_state.drive_actions()

    assert player.status_manager.status == StatusType.WRATH
    assert len(player.card_manager.get_pile("hand")) == 2
