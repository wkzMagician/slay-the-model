from actions.combat import AttackAction, DealDamageAction, GainBlockAction
from enemies.act1.cultist import Cultist
from powers.base import Power
from powers.definitions.thievery import ThieveryPower
from tests.test_combat_utils import create_test_helper
from utils.result_types import MultipleActionsResult, SingleActionResult


def test_card_actions_import_from_split_modules():
    from actions.combat import AttackAction as CombatAttackAction
    from actions.combat import DealDamageAction as CombatDealDamageAction
    from actions.combat_cards import AttackAction as SplitAttackAction
    from actions.combat_damage import DealDamageAction as SplitDealDamageAction

    assert CombatAttackAction is SplitAttackAction
    assert CombatDealDamageAction is SplitDealDamageAction


def _capture_published_message_types(game_state, monkeypatch):
    original_publish = game_state.publish_message
    published = []

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", wrapped)
    return published


class _AttackBlockPower(Power):
    def on_attack(self, target=None, source=None, card=None):
        return [GainBlockAction(block=4, target=source)]


def test_attack_action_publishes_attack_performed_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=60, max_hp=80, energy=3)
    player.gold = 99
    enemy = helper.create_enemy(Cultist, hp=30)
    enemy.add_power(ThieveryPower(amount=15, owner=enemy))
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = AttackAction(damage=6, target=player, source=enemy).execute()

    assert "AttackPerformedMessage" in published
    assert player.gold == 84
    assert isinstance(result, SingleActionResult)
    assert isinstance(result.action, DealDamageAction)


def test_attack_action_places_attack_hook_actions_before_damage(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=60, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    enemy.add_power(_AttackBlockPower(amount=0, owner=enemy))
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = AttackAction(damage=6, target=player, source=enemy).execute()

    assert "AttackPerformedMessage" in published
    assert isinstance(result, MultipleActionsResult)
    assert len(result.actions) == 2
    assert isinstance(result.actions[0], GainBlockAction)
    assert isinstance(result.actions[1], DealDamageAction)

