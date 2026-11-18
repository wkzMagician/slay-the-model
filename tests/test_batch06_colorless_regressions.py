from cards.colorless.apotheosis import Apotheosis
from cards.colorless.burn import Burn
from cards.colorless.dark_shackles import DarkShackles
from cards.colorless.deep_breath import DeepBreath
from cards.colorless.discovery import Discovery
from cards.colorless.enlightenment import Enlightenment
from cards.colorless.madness import Madness
from cards.colorless.necronomicurse import Necronomicurse
from cards.colorless.normality import Normality
from cards.colorless.parasite import Parasite
from cards.colorless.secret_technique import SecretTechnique
from cards.colorless.secret_weapon import SecretWeapon
from cards.ironclad.bash import Bash
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from cards.silent.neutralize import Neutralize
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType
from utils.types import CardType


def test_deep_breath_only_shuffles_discard_and_draws():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    in_hand = Strike()
    in_discard = Defend()
    helper.add_card_to_hand(in_hand)
    helper.add_card_to_discard_pile(in_discard)
    card = DeepBreath()
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True

    assert in_hand in player.card_manager.get_pile("hand")
    assert in_discard in player.card_manager.get_pile("hand")


def test_apotheosis_upgrades_hand_draw_discard_and_exhaust():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    hand_card = Strike()
    draw_card = Bash()
    discard_card = Defend()
    exhaust_card = Neutralize()
    player.card_manager.add_to_pile(hand_card, "hand", PilePosType.TOP)
    player.card_manager.add_to_pile(draw_card, "draw_pile", PilePosType.TOP)
    player.card_manager.add_to_pile(discard_card, "discard_pile", PilePosType.TOP)
    player.card_manager.add_to_pile(exhaust_card, "exhaust_pile", PilePosType.TOP)
    card = Apotheosis()
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True

    assert hand_card.upgrade_level == 1
    assert draw_card.upgrade_level == 1
    assert discard_card.upgrade_level == 1
    assert exhaust_card.upgrade_level == 1


def test_discovery_is_not_restricted_to_colorless_pool(monkeypatch):
    captured = {}

    def fake_fixed_choices(total, namespaces, rarities, card_types, pool_kind, rng):
        captured["namespaces"] = namespaces
        return [Strike()]

    monkeypatch.setattr("actions.card_choice.fixed_choices", fake_fixed_choices)

    helper = create_test_helper()
    helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    card = Discovery()
    helper.add_card_to_hand(card)
    assert helper.play_card(card) is True
    assert captured["namespaces"] is None


def test_enlightenment_only_reduces_costs_above_one():
    helper = create_test_helper()
    helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    zero = Neutralize()
    one = Strike()
    two = Bash()
    helper.add_card_to_hand(zero)
    helper.add_card_to_hand(one)
    helper.add_card_to_hand(two)
    card = Enlightenment()
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True

    assert zero.cost == 0
    assert one.cost == 1
    assert two.cost == 1


def test_normality_blocks_fourth_play_while_in_hand():
    helper = create_test_helper()
    player = helper.create_player(energy=10)
    helper.start_combat([helper.create_enemy(Cultist, hp=50)])

    normality = Normality()
    player.card_manager.add_to_pile(normality, "hand", PilePosType.TOP)
    player.card_manager.add_to_pile(Strike(), "hand", PilePosType.TOP)
    player.card_manager.add_to_pile(Strike(), "hand", PilePosType.TOP)
    player.card_manager.add_to_pile(Strike(), "hand", PilePosType.TOP)
    fourth = Strike()
    player.card_manager.add_to_pile(fourth, "hand", PilePosType.TOP)

    hand = player.card_manager.get_pile("hand")
    for card in list(hand):
        if isinstance(card, Strike) and card is not fourth:
            combat = helper.game_state.current_combat
            assert combat is not None
            assert helper.play_card(card, combat.enemies[0]) is True

    can_play, _ = fourth.can_play()
    assert can_play is False


def test_turn_cards_played_does_not_report_normality_restriction_without_normality():
    helper = create_test_helper()
    helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    combat = helper.game_state.current_combat
    assert combat is not None
    combat.combat_state.turn_cards_played = 3

    can_play, reason = Strike().can_play()

    assert can_play is True
    assert reason is None


def test_burn_triggers_at_end_of_turn():
    helper = create_test_helper()
    player = helper.create_player(energy=3, hp=40, max_hp=40)
    combat = helper.start_combat([helper.create_enemy(Cultist, hp=30)])
    burn = Burn()
    helper.add_card_to_hand(burn)

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert player.hp == 38


def test_necronomicurse_returns_to_hand_when_exhausted():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    curse = Necronomicurse()
    helper.add_card_to_hand(curse)
    from actions.card_lifecycle import ExhaustCardAction

    ExhaustCardAction(curse, source_pile="hand").execute()
    helper.game_state.drive_actions()

    assert any(isinstance(card, Necronomicurse) for card in player.card_manager.get_pile("hand"))


def test_parasite_removal_costs_max_hp():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    curse = Parasite()
    player.card_manager.add_to_pile(curse, "deck", PilePosType.TOP)
    from actions.card_lifecycle import RemoveCardAction

    RemoveCardAction(curse, "deck").execute()
    helper.game_state.drive_actions()

    assert player.max_hp == 77


def test_dark_shackles_returns_strength_at_end_of_turn():
    helper = create_test_helper()
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])
    card = DarkShackles()
    helper.add_card_to_hand(card)

    assert helper.play_card(card, enemy) is True

    assert enemy.get_power("Strength").amount == -9
    assert enemy.get_power("Strength Up").amount == 9


def test_secret_technique_requires_skill_in_draw_pile():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    attack = Strike()
    player.card_manager.add_to_pile(attack, "draw_pile", PilePosType.TOP)
    card = SecretTechnique()

    can_play, _ = card.can_play()
    assert can_play is False

    player.card_manager.add_to_pile(Defend(), "draw_pile", PilePosType.TOP)
    can_play, _ = card.can_play()
    assert can_play is True


def test_secret_weapon_requires_attack_in_draw_pile():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    player.card_manager.add_to_pile(Defend(), "draw_pile", PilePosType.TOP)
    card = SecretWeapon()

    can_play, _ = card.can_play()
    assert can_play is False

    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
    can_play, _ = card.can_play()
    assert can_play is True


def test_madness_only_targets_cards_that_can_be_reduced():
    helper = create_test_helper()
    helper.create_player(energy=3)
    helper.start_combat([helper.create_enemy(Cultist, hp=30)])

    zero_cost = Neutralize()
    two_cost = Bash()
    helper.add_card_to_hand(zero_cost)
    helper.add_card_to_hand(two_cost)
    card = Madness()
    helper.add_card_to_hand(card)

    assert helper.play_card(card) is True

    assert zero_cost.cost == 0
    assert two_cost.cost == 0
