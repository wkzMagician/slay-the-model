"""Unit tests for power stacking semantics in Creature.add_power."""

import sys

sys.path.insert(0, "D:/game/slay-the-model")

from entities.creature import Creature
from powers.base import Power, StackType


class DurationPower(Power):
    name = "Duration Test"
    stack_type = StackType.DURATION


class IntensityPower(Power):
    name = "Intensity Test"
    stack_type = StackType.INTENSITY


class PresencePower(Power):
    name = "Presence Test"
    stack_type = StackType.PRESENCE


class BothPower(Power):
    name = "Both Test"
    stack_type = StackType.BOTH


class LinkedPower(Power):
    name = "Linked Test"
    stack_type = StackType.LINKED
    amount_equals_duration = True


class SynchronizedIntensityPower(Power):
    name = "Synchronized Intensity Test"
    stack_type = StackType.INTENSITY
    amount_equals_duration = True


class MultiInstancePower(Power):
    name = "Multi Test"
    stack_type = StackType.MULTI_INSTANCE


def test_duration_stacks_only_duration():
    creature = Creature(max_hp=100)
    creature.add_power(DurationPower(amount=9, duration=2))
    creature.add_power(DurationPower(amount=5, duration=3))

    power = creature.get_power("Duration Test")
    assert power is not None
    assert power.duration == 5
    assert power.amount == 9


def test_intensity_stacks_only_amount():
    creature = Creature(max_hp=100)
    creature.add_power(IntensityPower(amount=2, duration=-1))
    creature.add_power(IntensityPower(amount=3, duration=4))

    power = creature.get_power("Intensity Test")
    assert power is not None
    assert power.amount == 5
    assert power.duration == -1


def test_presence_does_not_duplicate():
    creature = Creature(max_hp=100)
    creature.add_power(PresencePower(amount=1, duration=-1))
    creature.add_power(PresencePower(amount=99, duration=-1))

    matches = [p for p in creature.powers if p.name == "Presence Test"]
    assert len(matches) == 1


def test_both_stacks_amount_and_duration():
    creature = Creature(max_hp=100)
    creature.add_power(BothPower(amount=2, duration=3))
    creature.add_power(BothPower(amount=4, duration=5))

    power = creature.get_power("Both Test")
    assert power is not None
    assert power.amount == 6
    assert power.duration == 8


def test_linked_stacks_in_sync():
    creature = Creature(max_hp=100)
    creature.add_power(LinkedPower(amount=3, duration=3))
    creature.add_power(LinkedPower(amount=2, duration=2))

    power = creature.get_power("Linked Test")
    assert power is not None
    assert power.duration == 5
    assert power.amount == 5


def test_multi_instance_allows_duplicates():
    creature = Creature(max_hp=100)
    creature.add_power(MultiInstancePower(amount=10, duration=3))
    creature.add_power(MultiInstancePower(amount=20, duration=5))

    matches = [p for p in creature.powers if p.name == "Multi Test"]
    assert len(matches) == 2


def test_intensity_stacking_keeps_amount_and_duration_in_sync_when_linked_by_property():
    creature = Creature(max_hp=100)
    creature.add_power(SynchronizedIntensityPower(amount=1, duration=1))
    creature.add_power(SynchronizedIntensityPower(amount=2, duration=2))

    power = creature.get_power("Synchronized Intensity Test")
    assert power is not None
    assert power.amount == 3
    assert power.duration == 3
