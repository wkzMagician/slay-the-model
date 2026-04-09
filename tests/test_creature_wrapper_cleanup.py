from entities.creature import Creature


def test_creature_no_longer_exposes_legacy_damage_wrappers():
    creature = Creature(max_hp=20)

    assert not hasattr(creature, "on_damage_taken")
    assert not hasattr(creature, "on_lose_hp")
