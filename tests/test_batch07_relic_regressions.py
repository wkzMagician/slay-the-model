import random
from unittest.mock import MagicMock
from typing import cast

import pytest

from actions.card import AddCardAction, ExhaustCardAction
from actions.combat import AddEnemyAction, DealDamageAction, LoseHPAction
from actions.reward import AddRandomRelicAction, AddRelicAction
from cards.colorless.doubt import Doubt
from cards.colorless.shiv import Shiv
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from enemies.act2.the_collector import TorchHead
from orbs.frost import FrostOrb
from powers.definitions.poison import PoisonPower
from powers.definitions.pen_nib import PenNibPower
from powers.definitions.weak import WeakPower
from relics.character.defect import GoldPlatedCables, RunicCapacitor
from relics.character.ironclad import Runicube
from relics.character.silent import PaperKrane, RingOfTheSerpent, TwistedFunnel
from relics.global_relics.boss import PhilosophersStone
from relics.global_relics.common import Anchor, CeramicFish, Omamori, PenNib
from relics.global_relics.rare import DeadBranch, Torii
from relics.global_relics.uncommon import (
    DarkstonePeriapt,
    GremlinHorn,
    Matryoshka,
    MummifiedHand,
)
from tests.test_combat_utils import create_test_helper
from utils.types import CardType, PilePosType, RarityType


def test_gremlin_horn_does_not_trigger_on_final_kill():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=1, max_energy=3)
    player.relics.append(GremlinHorn())
    enemy = helper.create_enemy(Cultist, hp=6)
    helper.start_combat([enemy])

    attack = Strike()
    helper.add_card_to_hand(attack)
    helper.play_card(attack, target=enemy)
    helper.game_state.drive_actions()

    assert enemy.is_dead()
    assert player.energy == 0
    assert len(player.card_manager.get_pile("hand")) == 0


def test_dead_branch_does_not_create_cards_after_combat_has_ended():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(DeadBranch())
    enemy = helper.create_enemy(Cultist, hp=1)
    combat = helper.start_combat([enemy])

    enemy.hp = 0
    combat._check_combat_end()
    helper.game_state.drive_actions()

    exhaust_target = Strike()
    helper.add_card_to_hand(exhaust_target)

    ExhaustCardAction(card=exhaust_target, source_pile="hand").execute()
    helper.game_state.drive_actions()

    assert exhaust_target in player.card_manager.get_pile("exhaust_pile")
    assert len(player.card_manager.get_pile("hand")) == 0


def test_mummified_hand_only_selects_positive_cost_cards(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = MummifiedHand()
    player.relics.append(relic)

    zero_cost = Shiv()
    paid_card = Strike()
    helper.add_card_to_hand(zero_cost)
    helper.add_card_to_hand(paid_card)

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    relic.on_card_play(Inflame(), [])

    assert zero_cost.cost_until_end_of_turn is None
    assert paid_card.cost_until_end_of_turn == 0


def test_pen_nib_primes_after_ninth_attack():
    relic = PenNib()
    player = MagicMock()
    attack_card = MagicMock()
    attack_card.card_type = CardType.ATTACK

    from engine.game_state import game_state

    game_state.action_queue.clear()
    for _ in range(8):
        relic.on_card_play(attack_card, [])
        assert game_state.action_queue.is_empty()

    relic.on_card_play(attack_card, [])
    assert len(game_state.action_queue.queue) == 1
    queued = game_state.action_queue.queue[0]
    assert getattr(queued, "power", None).__class__ is PenNibPower


def test_anchor_applies_block_during_combat_start():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(Anchor())
    enemy = helper.create_enemy(Cultist, hp=20)

    helper.start_combat([enemy])
    helper.game_state.drive_actions()

    assert player.block == 10


def test_runic_capacitor_grants_slots_on_first_turn_start_only():
    helper = create_test_helper()
    player = helper.create_player(hp=75, max_hp=75, energy=3)
    player.namespace = "defect"
    player.relics.append(RunicCapacitor())
    combat = helper.start_combat([])

    assert player.orb_manager.max_orb_slots == 1

    combat._start_player_turn()
    helper.game_state.drive_actions()

    assert player.orb_manager.max_orb_slots == 4


def test_gold_plated_cables_triggers_leftmost_orb_extra_time():
    helper = create_test_helper()
    player = helper.create_player(hp=75, max_hp=75, energy=3)
    player.namespace = "defect"
    player.relics.append(GoldPlatedCables())
    combat = helper.start_combat([])
    player.orb_manager.max_orb_slots = 2
    player.orb_manager.add_orb(FrostOrb())
    player.orb_manager.add_orb(FrostOrb())
    player.block = 0

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert player.block == 6


def test_ceramic_fish_only_triggers_for_deck_card_gain():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(CeramicFish())
    initial_gold = player.gold

    AddCardAction(card=Strike(), dest_pile="hand", source="reward").execute()
    helper.game_state.drive_actions()

    assert player.gold == initial_gold

    AddCardAction(card=Strike(), dest_pile="deck", source="reward").execute()
    helper.game_state.drive_actions()

    assert player.gold == initial_gold + 9


def test_darkstone_periapt_only_triggers_for_deck_curse_gain():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(DarkstonePeriapt())
    initial_max_hp = player.max_hp

    AddCardAction(card=Doubt(), dest_pile="hand", source="reward").execute()
    helper.game_state.drive_actions()

    assert player.max_hp == initial_max_hp

    AddCardAction(card=Doubt(), dest_pile="deck", source="reward").execute()
    helper.game_state.drive_actions()

    assert player.max_hp == initial_max_hp + 6


def test_matryoshka_large_chest_never_requests_rare_relic(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = Matryoshka()
    player.relics.append(relic)

    monkeypatch.setattr(random, "random", lambda: 0.99)

    relic.on_chest_open("large")

    queued = helper.game_state.action_queue.peek_next()
    assert isinstance(queued, AddRandomRelicAction)
    queued = cast(AddRandomRelicAction, queued)
    assert queued.rarities == [RarityType.UNCOMMON]


def test_omamori_negates_curse_without_removing_relic():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = Omamori()
    player.relics.append(relic)

    AddCardAction(card=Doubt(), dest_pile="deck", source="reward").execute()
    AddCardAction(card=Doubt(), dest_pile="deck", source="reward").execute()
    helper.game_state.drive_actions()

    assert relic in player.relics
    assert relic.curses_to_negate == 0
    assert player.card_manager.get_pile("deck") == []


def test_ring_of_the_serpent_increases_base_draw_count_when_obtained():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)

    AddRelicAction(RingOfTheSerpent()).execute()
    helper.game_state.drive_actions()

    assert player.base_draw_count == 6


def test_philosophers_stone_applies_strength_to_spawned_enemy():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(PhilosophersStone())
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    helper.game_state.drive_actions()

    summoned = TorchHead()
    AddEnemyAction(summoned).execute()
    helper.game_state.drive_actions()

    strength = summoned.get_power("Strength")
    assert strength is not None
    assert strength.amount == 1


def test_torii_only_reduces_attack_damage():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    player.relics.append(Torii())
    helper.start_combat([enemy])

    DealDamageAction(damage=5, target=player, source=enemy, damage_type="attack").execute()
    helper.game_state.drive_actions()
    assert player.hp == 79

    player.hp = 80
    DealDamageAction(damage=5, target=player, source=enemy, damage_type="direct").execute()
    helper.game_state.drive_actions()
    assert player.hp == 75


def test_twisted_funnel_applies_four_poison():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    player.relics.append(TwistedFunnel())
    helper.start_combat([enemy])
    helper.game_state.drive_actions()

    poison = enemy.get_power("Poison")
    assert isinstance(poison, PoisonPower)
    assert poison.amount == 4


def test_runic_cube_draws_when_hp_is_lost_without_damage():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics.append(Runicube())
    enemy = helper.create_enemy(Cultist, hp=20)
    helper.start_combat([enemy])
    player.card_manager.get_pile("draw_pile").clear()
    player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)

    LoseHPAction(amount=3, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert player.hp == 77
    assert len(player.card_manager.get_pile("hand")) == 1


def test_paper_krane_makes_weak_enemy_deal_40_percent_less_damage():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    player.relics.append(PaperKrane())
    helper.start_combat([enemy])
    enemy.add_power(WeakPower(duration=1, owner=enemy))

    DealDamageAction(damage=8, target=player, source=enemy, damage_type="attack").execute()
    helper.game_state.drive_actions()

    assert player.hp == 76
