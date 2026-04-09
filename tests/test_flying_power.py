"""Tests for FlyingPower behavior."""
import sys

sys.path.insert(0, "D:/game/slay-the-model")

from enemies.act2.byrd import Byrd
from powers.definitions.flying import FlyingPower


def test_flying_halves_incoming_damage():
    power = FlyingPower(amount=3)
    assert power.modify_damage_taken(10) == 5
    assert power.modify_damage_taken(1) == 0


def test_flying_loses_stack_only_on_attack_damage():
    power = FlyingPower(amount=2)

    assert power.amount == 2

    power.on_physical_attack_taken(5)
    assert power.amount == 1


def test_flying_zero_stacks_grounds_and_forces_stunned():
    byrd = Byrd()
    byrd._is_flying = True
    byrd._grounded_pattern_index = 0
    byrd.current_intention = byrd.intentions["peck"]

    power = FlyingPower(amount=1, owner=byrd)
    power.on_physical_attack_taken(4)

    assert power.amount == 0
    assert byrd._is_flying is False
    assert byrd.current_intention.name == "stunned"
    assert byrd._grounded_pattern_index == 1
