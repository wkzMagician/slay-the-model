"""REL-020: Red Skull threshold reactions precede the next queued action."""

import pytest

from actions.base import LambdaAction
from actions.combat_damage import HealAction, LoseHPAction
from enemies.act1.cultist import Cultist
from potions.global_potions import FairyInABottle
from relics.base import Relic
from relics.character.ironclad import MagicFlower, RedSkull
from relics.global_relics.rare import LizardTail
from tests.test_combat_utils import create_test_helper


def setup_combat(hp=54, max_hp=100, earlier_relics=()):
    helper = create_test_helper()
    player = helper.create_player(hp=hp, max_hp=max_hp)
    player.base_draw_count = 0
    skull = RedSkull()
    player.relics = [*earlier_relics, skull]
    helper.start_combat([Cultist()])
    assert helper.game_state.drive_actions() is None
    return helper, player, skull


@pytest.mark.parametrize("max_hp,hp,active", [
    (100, 49, True), (100, 50, True), (100, 51, False),
    (99, 49, True), (99, 50, False),
])
def test_opening_half_hp_boundary(max_hp, hp, active):
    _, player, skull = setup_combat(hp=hp, max_hp=max_hp)
    assert skull.strength_applied is active
    assert player.strength == (3 if active else 0)


class OpeningHeal(Relic):
    def on_combat_start(self, floor):
        from engine.runtime_api import add_action
        add_action(HealAction(amount=5))


def test_opening_check_uses_hp_after_earlier_opening_actions():
    _, player, skull = setup_combat(hp=48, earlier_relics=[OpeningHeal()])
    assert player.hp == 53
    assert player.strength == 0
    assert not skull.strength_applied


@pytest.mark.parametrize("max_hp,hp,loss,expected_strength", [
    (100, 54, 4, 3), (100, 54, 3, 0),
    (99, 52, 3, 3), (99, 52, 2, 0),
])
def test_hp_loss_reacts_before_next_action(max_hp, hp, loss, expected_strength):
    helper, player, skull = setup_combat(hp=hp, max_hp=max_hp)
    seen = []
    helper.game_state.add_actions([
        LoseHPAction(amount=loss),
        LambdaAction(lambda: seen.append(player.strength)),
    ])
    assert helper.game_state.drive_actions() is None
    assert seen == [expected_strength]
    assert skull.strength_applied == bool(expected_strength)


@pytest.mark.parametrize("max_hp,hp,heal,expected_strength", [
    (100, 48, 2, 3), (100, 48, 3, 0),
    (100, 40, 6, 3), (99, 48, 1, 3), (99, 48, 2, 0),
])
def test_heal_reacts_before_next_action_without_double_counting_amount(
        max_hp, hp, heal, expected_strength):
    helper, player, skull = setup_combat(hp=hp, max_hp=max_hp)
    seen = []
    helper.game_state.add_actions([
        HealAction(amount=heal),
        LambdaAction(lambda: seen.append(player.strength)),
    ])
    assert helper.game_state.drive_actions() is None
    assert seen == [expected_strength]
    assert skull.strength_applied == bool(expected_strength)


def test_repeated_threshold_crossings_do_not_duplicate_strength():
    helper, player, skull = setup_combat(hp=51)
    seen = []
    actions = []
    for action in [LoseHPAction(amount=1), LoseHPAction(amount=1), HealAction(amount=2),
                   HealAction(amount=1), LoseHPAction(amount=2)]:
        actions.extend([action, LambdaAction(lambda: seen.append(player.strength))])
    helper.game_state.add_actions(actions)
    assert helper.game_state.drive_actions() is None
    assert seen == [3, 3, 0, 0, 3]
    assert skull.strength_applied


@pytest.mark.parametrize("save,flower,expected_hp,expected_strength", [
    ("fairy", False, 30, 3), ("fairy", True, 45, 3),
    ("tail", False, 50, 3), ("tail", True, 75, 0),
])
def test_reviving_heal_reconciles_pending_threshold_changes(
        save, flower, expected_hp, expected_strength):
    helper, player, skull = setup_combat(hp=54)
    if save == "fairy":
        player.potions.append(FairyInABottle())
    else:
        player.relics.append(LizardTail())
    if flower:
        player.relics.append(MagicFlower())
    seen = []
    helper.game_state.add_actions([
        LoseHPAction(amount=54),
        LambdaAction(lambda: seen.append((player.hp, player.strength))),
    ])
    assert helper.game_state.drive_actions() is None
    assert seen == [(expected_hp, expected_strength)]
    assert skull.strength_applied == bool(expected_strength)


def test_outside_combat_loss_does_not_queue_strength():
    helper = create_test_helper()
    player = helper.create_player(hp=51, max_hp=100)
    skull = RedSkull()
    player.relics = [skull]
    LoseHPAction(amount=1).execute()
    assert helper.game_state.drive_actions() is None
    assert player.strength == 0
    assert not skull.strength_applied


def test_victory_resets_activation_and_ended_combat_cannot_reactivate():
    helper, player, skull = setup_combat(hp=40)
    skull.on_combat_end()
    combat = helper.game_state.current_combat
    assert combat is not None
    combat.combat_ended = True
    skull.on_any_hp_lost(1)
    assert not skull.strength_applied
    assert helper.game_state.action_queue.is_empty()
