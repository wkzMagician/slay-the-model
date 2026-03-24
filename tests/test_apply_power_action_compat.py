from actions.combat import ApplyPowerAction
from enemies.act2.the_champ import TheChamp
from powers.definitions.metallicize import MetallicizePower


def test_apply_power_action_surface_matches_split_module():
    from actions.combat import ApplyPowerAction as CombatApplyPowerAction
    from actions.combat_status import ApplyPowerAction as SplitApplyPowerAction

    assert CombatApplyPowerAction is SplitApplyPowerAction


def test_apply_power_action_accepts_power_class():
    enemy = TheChamp()

    ApplyPowerAction(MetallicizePower, enemy, amount=5, duration=-1).execute()

    power = enemy.get_power('Metallicize')
    assert power is not None
    assert power.amount == 5

