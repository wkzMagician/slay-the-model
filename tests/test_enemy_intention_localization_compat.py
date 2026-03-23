from enemies.act3.nemesis import Nemesis
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
