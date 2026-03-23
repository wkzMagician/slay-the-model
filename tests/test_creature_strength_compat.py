from enemies.act3.nemesis import Nemesis
from powers.definitions.strength import StrengthPower


def test_creature_strength_property_reads_strength_power_amount():
    enemy = Nemesis()
    enemy.add_power(StrengthPower(amount=4, owner=enemy))

    assert enemy.strength == 4
