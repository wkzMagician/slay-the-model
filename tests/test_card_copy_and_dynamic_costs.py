"""LGT-012/CARD-029: independent snapshots and legal dynamic cost writes."""
import pytest
from typing import cast

from actions.autoplay import make_replay_copy
from actions.card import ChooseUpgradeCardAction, DiscardCardAction, DrawCardsAction
from actions.card_choice import SetNightmarePowerAction
from actions.combat_cards import PlayCardBHAction
from actions.display import InputRequestAction
from cards.base import Card
from cards.colorless.enlightenment import Enlightenment
from cards.colorless.madness import Madness
from cards.defect.defragment import Defragment
from cards.defect.force_field import ForceField
from cards.ironclad.bash import Bash
from cards.ironclad.flex import Flex
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from cards.silent.deadly_poison import DeadlyPoison
from cards.silent.eviscerate import Eviscerate
from cards.silent.bullet_time import BulletTime
from cards.colorless.forethought import Forethought
from cards.watcher.swivel import Swivel
from tests.test_combat_utils import create_test_helper
from enemies.act1.cultist import Cultist


def setup():
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100, energy=20)
    enemy = helper.create_enemy(Cultist, hp=100)
    combat = helper.start_combat([enemy])
    helper.game_state.drive_actions()
    return helper.game_state, player, enemy, combat


@pytest.mark.parametrize("factory,key,value", [(Inflame, "strength", 2),
                         (Bash, "vulnerable", 2), (Flex, "temp_strength", 2),
                         (DeadlyPoison, "poison", 5)])
def test_upgrade_preview_does_not_mutate_original(factory, key, value):
    gs, player, _, _ = setup()
    original = factory()
    player.card_manager.piles["deck"] = [original]
    before = original.get_magic_value(key)
    ChooseUpgradeCardAction(pile="deck").execute()
    assert original.get_magic_value(key) == before == value
    assert original.upgrade_level == 0
    request = cast(InputRequestAction, gs.action_queue.peek_next())
    assert isinstance(request, InputRequestAction)
    assert '->' in str(request.options[0].name)


@pytest.mark.parametrize("factory", [Inflame, Bash, Flex, DeadlyPoison])
def test_combat_copy_upgrade_does_not_change_permanent_card(factory):
    gs, player, _, _ = setup()
    original = factory()
    before = dict(original._magic)
    player.card_manager.piles["deck"] = [original]
    player.card_manager.reset_for_combat()
    copy = player.card_manager.get_pile("draw_pile")[0]
    copy.upgrade()
    assert original._magic == before and original.upgrade_level == 0
    assert getattr(copy, "origin_card") is original


@pytest.mark.parametrize("factory", [Inflame, Bash, Flex, DeadlyPoison])
def test_nightmare_snapshot_and_three_results_are_independent(factory):
    gs, player, _, _ = setup()
    original = factory()
    snapshot = dict(original._magic)
    SetNightmarePowerAction(original).execute()
    original.upgrade()
    power = player.get_power("Nightmare")
    assert power is not None
    power.on_turn_start()
    gs.drive_actions()
    copies = list(player.card_manager.get_pile("hand"))
    assert len(copies) == 3
    assert all(c._magic == snapshot and c.upgrade_level == 0 for c in copies)
    copies[0]._magic['probe'] = 99
    assert all('probe' not in c._magic for c in copies[1:])


@pytest.mark.parametrize("copier", [lambda c: c.copy(), make_replay_copy])
def test_nested_card_state_is_copied_without_cloning_external_objects(copier):
    _, _, enemy, _ = setup()
    original = Inflame()
    setattr(original, "state", {"levels": [1], "targets": [enemy]})
    clone = copier(original)
    getattr(clone, 'state')['levels'].append(2)
    assert getattr(original, 'state')['levels'] == [1]
    assert getattr(clone, 'state')['targets'][0] is enemy


@pytest.mark.parametrize("factory", [Eviscerate, ForceField])
def test_madness_can_write_dynamic_cost_and_pay_zero(factory):
    gs, player, enemy, _ = setup()
    target = factory()
    madness = Madness()
    madness.upgrade()
    player.card_manager.piles["hand"] = [madness, target]
    gs.add_action(PlayCardBHAction(madness, []))
    gs.drive_actions()
    assert target.cost == 0
    before = player.energy
    gs.add_action(PlayCardBHAction(target, [enemy]))
    gs.drive_actions()
    assert player.energy == before


@pytest.mark.parametrize("factory", [Eviscerate, ForceField])
@pytest.mark.parametrize("upgraded", [False, True])
def test_enlightenment_writes_cost_and_resets_only_temporary_change(factory, upgraded):
    gs, player, _, _ = setup()
    target = factory()
    card = Enlightenment()
    if upgraded:
        card.upgrade()
    player.card_manager.piles["hand"] = [card, target]
    gs.add_action(PlayCardBHAction(card, []))
    gs.drive_actions()
    assert target.cost == 1
    target.cost_until_end_of_turn = None
    assert target.cost == (1 if upgraded else target.base_cost)


def test_eviscerate_obeys_bullet_time_actual_energy_payment():
    gs, player, enemy, _ = setup()
    target = Eviscerate()
    bullet = BulletTime()
    player.card_manager.piles["hand"] = [bullet, target]
    gs.add_action(PlayCardBHAction(bullet, []))
    gs.drive_actions()
    before = player.energy
    gs.add_action(PlayCardBHAction(target, [enemy]))
    gs.drive_actions()
    assert player.energy == before and enemy.hp == 79


def test_dynamic_reductions_continue_after_enlightenment():
    gs, player, _, _ = setup()
    force = ForceField()
    evi = Eviscerate()
    enlightenment = Enlightenment()
    enlightenment.upgrade()
    filler = Strike()
    player.card_manager.piles["hand"] = [force, evi, enlightenment, filler]
    gs.add_action(PlayCardBHAction(enlightenment, []))
    gs.drive_actions()
    gs.add_action(DiscardCardAction(filler, source_pile="hand"))
    gs.drive_actions()
    assert evi.cost == 0
    power = Defragment()
    player.card_manager.piles["hand"].append(power)
    gs.add_action(PlayCardBHAction(power, []))
    gs.drive_actions()
    assert force.cost == 0
    force.cost_until_end_of_turn = None
    assert force.cost == 0


@pytest.mark.parametrize("factory", [Eviscerate, ForceField])
def test_once_free_takes_priority_over_turn_override(factory):
    _, _, _, _ = setup()
    card = factory()
    card.cost_until_end_of_turn = 1
    card.cost_until_played = 0
    assert card.cost == 0


def test_eviscerate_redraw_uses_base_minus_discards_and_keeps_once_free():
    gs, player, _, combat = setup()
    card = Eviscerate()
    filler = Strike()
    player.card_manager.piles["hand"] = [card, filler]
    gs.add_action(DiscardCardAction(filler, source_pile="hand"))
    gs.drive_actions()
    assert card.cost == 2
    card.cost_until_played = 0
    player.card_manager.move_to(card, 'draw_pile', src='hand')
    gs.add_action(DrawCardsAction(count=1))
    gs.drive_actions()
    assert card.cost == 0
    card.cost_until_played = None
    assert card.cost == 2
    combat.combat_state.reset_turn_info()
    card.cost_until_end_of_turn = None
    assert card.cost == 3


@pytest.mark.parametrize("factory", [Eviscerate, ForceField])
def test_nightmare_resets_turn_cost_but_keeps_base_and_once_free(factory):
    gs, player, _, _ = setup()
    card = factory()
    card.cost = 2
    card.cost_until_end_of_turn = 1
    card.cost_until_played = 0
    SetNightmarePowerAction(card).execute()
    power = player.get_power('Nightmare')
    assert power is not None
    snapshot = power.stored_card
    assert snapshot is not card
    assert snapshot.cost_until_end_of_turn is None
    assert snapshot._cost == 2 and snapshot.cost_until_played == 0
    assert card.cost_until_end_of_turn == 1


def test_force_field_never_mutates_permanent_deck_or_exhausted_cards():
    gs, player, _, _ = setup()
    original = ForceField()
    player.card_manager.piles['deck'] = [original]
    player.card_manager.reset_for_combat()
    combat_card = player.card_manager.get_pile('draw_pile')[0]
    exhausted = ForceField()
    player.card_manager.piles['exhaust_pile'] = [exhausted]
    power = Defragment()
    player.card_manager.piles['hand'] = [power]
    gs.add_action(PlayCardBHAction(power, []))
    gs.drive_actions()
    assert combat_card.cost == 3
    assert original.cost == exhausted.cost == 4
    assert ForceField().cost == 3


@pytest.mark.parametrize("effect", [Forethought, Swivel])
def test_native_free_effects_keep_eviscerate_free_when_played(effect):
    gs, player, enemy, _ = setup()
    target = Eviscerate()
    producer = effect()
    player.card_manager.piles['hand'] = [producer, target]
    gs.add_action(PlayCardBHAction(producer, []))
    gs.drive_actions()
    if effect is Forethought:
        gs.add_action(DrawCardsAction(count=1))
        gs.drive_actions()
    assert target.cost == 0
    before = player.energy
    gs.add_action(PlayCardBHAction(target, [enemy]))
    gs.drive_actions()
    assert player.energy == before


@pytest.mark.parametrize("factory", [Eviscerate, ForceField])
def test_copy_keeps_independent_cost_flags(factory):
    _, _, _, _ = setup()
    card = factory()
    card.cost = 1
    card.cost_until_end_of_turn = 0
    card.cost_until_played = 0
    clone = card.copy()
    clone.cost = 2
    clone.cost_until_end_of_turn = 2
    clone.cost_until_played = None
    assert card._cost == 1 and card.cost == 0
    assert clone.cost == 2
