import re

import pytest

from enemies.act1.spike_slime import SpikeSlimeL
from enemies.act2.mugger import Mugger
from enemies.act2.spheric_guardian import SphericGuardian
from enemies.act2.the_champ import TheChamp
from enemies.act3.nemesis import Nemesis
from enemies.act3.repulsor import Repulsor
from enemies.act3.spiker import Spiker


def test_nemesis_tri_burn_description_localizes_without_raw_key():
    enemy = Nemesis()
    enemy.current_intention = enemy.intentions["Tri Burn"]

    desc = enemy.current_intention.description.resolve()

    assert desc
    assert not desc.startswith("enemies.")
    assert desc != "description"


def test_spiker_buff_thorns_description_localizes_without_raw_key():
    enemy = Spiker()
    enemy.current_intention = enemy.intentions["Buff Thorns"]

    desc = enemy.current_intention.description.resolve()

    assert desc
    assert not desc.startswith("enemies.")
    assert desc != "description"


@pytest.mark.parametrize(
    "enemy_factory,intention_key",
    [
        (Mugger, "mug"),
        (SpikeSlimeL, "lick"),
        (SphericGuardian, "debuff_attack"),
        (Repulsor, "Attack"),
        (TheChamp, "Defensive Stance"),
        (TheChamp, "Gloat"),
        (TheChamp, "Anger"),
    ],
)
def test_intention_description_has_no_unresolved_placeholders(enemy_factory, intention_key):
    enemy = enemy_factory()
    if hasattr(enemy, "on_combat_start"):
        enemy.on_combat_start(floor=1)
    enemy.current_intention = enemy.intentions[intention_key]

    desc = enemy.current_intention.description.resolve()

    assert desc
    assert not re.search(r"\{[a-zA-Z0-9_.]+\}", desc), desc
