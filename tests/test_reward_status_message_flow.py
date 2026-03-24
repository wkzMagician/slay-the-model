from actions.combat import ApplyPowerAction, GainBlockAction, HealAction, LoseHPAction, UsePotionBHAction
from actions.reward import AddGoldAction
from enemies.act1.cultist import Cultist
from engine.messages import HealedMessage
from potions.global_potions import BlockPotion
from powers.definitions.juggernaut import JuggernautPower
from powers.definitions.rupture import RupturePower
from relics.character.ironclad import ChampionBelt, RedSkull
from relics.global_relics.common import ToyOrnithopter
from relics.global_relics.event import BloodyIdol
from tests.test_combat_utils import create_test_helper
from utils.result_types import MultipleActionsResult, SingleActionResult


def test_status_actions_import_from_split_modules():
    from actions.combat import ApplyPowerAction as CombatApplyPowerAction
    from actions.combat import UsePotionBHAction as CombatUsePotionBHAction
    from actions.combat_status import ApplyPowerAction as SplitApplyPowerAction
    from actions.combat_status import UsePotionBHAction as SplitUsePotionBHAction

    assert CombatApplyPowerAction is SplitApplyPowerAction
    assert CombatUsePotionBHAction is SplitUsePotionBHAction


def _execute_result(result):
    if result is None:
        return

    if isinstance(result, SingleActionResult):
        _execute_result(result.action.execute())
        return

    if isinstance(result, MultipleActionsResult):
        for action in result.actions:
            _execute_result(action.execute())
        return

    if hasattr(result, "execute"):
        _execute_result(result.execute())


def _capture_published_message_types(game_state, monkeypatch):
    original_publish = game_state.publish_message
    published = []

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", wrapped)
    return published


def test_apply_power_action_publishes_power_applied_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    player.relics = [ChampionBelt()]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = ApplyPowerAction(power="Vulnerable", target=enemy, amount=1).execute()
    _execute_result(result)

    assert "PowerAppliedMessage" in published
    assert enemy.has_power("Vulnerable")
    assert enemy.has_power("Weak")


def test_use_potion_action_publishes_potion_used_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=40, max_hp=80, energy=3)
    player.relics = [ToyOrnithopter()]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    potion = BlockPotion()
    player.potions.append(potion)
    initial_hp = player.hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = UsePotionBHAction(potion=potion, targets=[player]).execute()
    _execute_result(result)

    assert "PotionUsedMessage" in published
    assert player.hp == initial_hp + 5
    assert potion not in player.potions


def test_add_gold_action_publishes_gold_gained_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=40, max_hp=80, energy=3)
    player.relics = [BloodyIdol()]
    initial_hp = player.hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = AddGoldAction(amount=12).execute()
    _execute_result(result)

    assert "GoldGainedMessage" in published
    assert player.gold == 111
    assert player.hp == initial_hp + 5


def test_heal_action_publishes_healed_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=35, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    initial_hp = player.hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = HealAction(amount=10, target=player).execute()
    _execute_result(result)

    assert "HealedMessage" in published
    assert player.hp == initial_hp + 10


def test_healed_message_runs_red_skull_response():
    helper = create_test_helper()
    player = helper.create_player(hp=35, max_hp=80, energy=3)
    red_skull = RedSkull()
    player.relics = [red_skull]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    red_skull.strength_applied = True
    _execute_result(ApplyPowerAction(power="Strength", target=player, amount=3).execute())

    actions = helper.game_state.publish_message(
        HealedMessage(target=player, amount=10, previous_hp=35, new_hp=45),
        participants=[player, red_skull],
    )
    assert len(actions) == 1
    action = actions[0]
    assert isinstance(action, ApplyPowerAction)
    assert action.target is player
    assert action.power.amount == -3


def test_heal_action_does_not_use_direct_red_skull_fallback(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=35, max_hp=80, energy=3)
    red_skull = RedSkull()
    player.relics = [red_skull]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    red_skull.strength_applied = True
    _execute_result(ApplyPowerAction(power="Strength", target=player, amount=3).execute())

    monkeypatch.setattr(helper.game_state, "publish_message", lambda message, *args, **kwargs: [])

    result = HealAction(amount=10, target=player).execute()
    _execute_result(result)

    assert player.strength == 3


def test_lose_hp_action_publishes_hp_lost_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.add_power(RupturePower(amount=1, owner=player))
    card = enemy  # just a non-None sentinel won't work with Rupture semantics
    from cards.ironclad.bloodletting import Bloodletting
    bloodletting = Bloodletting()

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = LoseHPAction(amount=3, target=player, card=bloodletting, source=bloodletting).execute()
    _execute_result(result)

    assert "HpLostMessage" in published
    assert player.hp == 77
    assert player.strength == 1


def test_gain_block_action_publishes_block_gained_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])
    player.add_power(JuggernautPower(amount=5, owner=player))

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    result = GainBlockAction(block=7, target=player).execute()
    _execute_result(result)

    assert "BlockGainedMessage" in published
    assert player.block == 7
    assert enemy.hp == 25

