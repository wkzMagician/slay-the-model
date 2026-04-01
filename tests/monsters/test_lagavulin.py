#!/usr/bin/env python
"""Tests for Lagavulin enemy."""

import unittest

from tests.test_combat_utils import CombatTestHelper
from enemies.act1.lagavulin import Lagavulin
from engine.messages import DamageResolvedMessage
from engine.message_bus import MessageBus


class TestLagavulin(unittest.TestCase):
    """Test Lagavulin enemy functionality."""

    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(energy=3)
        self.enemy = self.helper.create_enemy(Lagavulin, hp=110)

    def test_lagavulin_creation(self):
        """Test Lagavulin can be created."""
        self.assertIsInstance(self.enemy, Lagavulin)

    def test_lagavulin_has_intentions(self):
        """Test Lagavulin has intentions defined."""
        self.assertIsNotNone(self.enemy.intentions)

    def test_lagavulin_intention_on_combat_start(self):
        """Test Lagavulin starts with sleep intention."""
        self.enemy.on_combat_start(floor=1)
        self.assertIsNotNone(self.enemy.current_intention)
        self.assertEqual(self.enemy.current_intention.name, "sleep")

    def test_attack_pattern_after_wake(self):
        """Test Lagavulin attacks after waking from sleep."""
        # Create fresh enemy and start combat manually
        enemy = Lagavulin()
        enemy.on_combat_start(floor=1)
        
        # First intention is sleep
        self.assertEqual(enemy.current_intention.name, "sleep")

        # Second turn (still sleeping)
        enemy.on_player_turn_start()
        self.assertEqual(enemy.current_intention.name, "sleep")

        # Third turn (now attacks)
        enemy.on_player_turn_start()
        self.assertEqual(enemy.current_intention.name, "attack")

    def test_lagavulin_has_hp(self):
        """Test Lagavulin has correct HP."""
        self.assertEqual(self.enemy.hp, 110)

    def test_start_awake_has_no_metallicize(self):
        """Dead Adventurer-style spawn has no Metallicize power."""
        enemy = Lagavulin(start_awake=True)
        self.assertFalse(any(p.name == "Metallicize" for p in enemy.powers))

    def test_start_awake_no_opening_block(self):
        """start_awake does not gain opening Block from on_combat_start."""
        enemy = Lagavulin(start_awake=True)
        enemy.on_combat_start(floor=1)
        self.assertEqual(enemy.block, 0)

    def test_sleeping_starts_with_metallicize(self):
        """Default elite encounter has Metallicize while asleep."""
        enemy = Lagavulin(start_awake=False)
        self.assertTrue(any(p.name == "Metallicize" for p in enemy.powers))

    def test_sleeping_gets_opening_block_on_combat_start(self):
        """Sleeping entry gains 8 Block when combat starts."""
        enemy = Lagavulin(start_awake=False)
        enemy.on_combat_start(floor=1)
        self.assertEqual(enemy.block, 8)

    def test_direct_damage_wakes_immediately(self):
        """Any damage_type with HP loss wakes sleeping Lagavulin (e.g. direct)."""
        lagavulin = Lagavulin(start_awake=False)
        lagavulin.on_combat_start(floor=1)
        bus = MessageBus()
        bus.publish(
            DamageResolvedMessage(
                amount=5,
                target=lagavulin,
                source=None,
                card=None,
                damage_type="direct",
            ),
            participants=[lagavulin],
        )
        self.assertFalse(lagavulin.is_sleeping)
        self.assertEqual(lagavulin.current_intention.name, "stunned")
        self.assertFalse(any(p.name == "Metallicize" for p in lagavulin.powers))

    def test_attack_damage_sets_stunned_immediately(self):
        """Attack HP damage sets intention to stunned in the same resolution."""
        lagavulin = Lagavulin(start_awake=False)
        lagavulin.on_combat_start(floor=1)
        bus = MessageBus()
        bus.publish(
            DamageResolvedMessage(
                amount=7,
                target=lagavulin,
                source=None,
                card=None,
                damage_type="attack",
            ),
            participants=[lagavulin],
        )
        self.assertFalse(lagavulin.is_sleeping)
        self.assertEqual(lagavulin.current_intention.name, "stunned")
        self.assertFalse(any(p.name == "Metallicize" for p in lagavulin.powers))


if __name__ == "__main__":
    unittest.main()
