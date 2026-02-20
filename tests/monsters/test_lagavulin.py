"""Tests for Lagavulin - Act 1 Elite enemy.

Tests verify Lagavulin's unique behaviors:
- Sleeping state with 3-turn wake-up timer
- Immediate wake-up on damage taken
- Attack pattern after waking (Attack / Siphon Soul)
- Metallicize power during sleep
"""

import unittest
from enemies.act1.lagavulin import Lagavulin
from utils.types import EnemyType


class TestLagavulin(unittest.TestCase):
    """Test Lagavulin monster behaviors and intention patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.enemy_asc0 = Lagavulin(ascension=0)
        self.enemy_asc3 = Lagavulin(ascension=3)

    def test_intentions_registered(self):
        """Test that all intentions are registered."""
        intentions = ["sleep", "stunned", "attack", "siphon_soul"]
        for intention in intentions:
            self.assertIn(intention, self.enemy_asc0.intentions)

    def test_hp_range_ascension_0_2(self):
        """Test HP is in correct range for ascension 0-2."""
        self.assertGreaterEqual(self.enemy_asc0.max_hp, 109)
        self.assertLessEqual(self.enemy_asc0.max_hp, 111)

    def test_hp_range_ascension_3_plus(self):
        """Test HP is in correct range for ascension 3+."""
        self.assertGreaterEqual(self.enemy_asc3.max_hp, 112)
        self.assertLessEqual(self.enemy_asc3.max_hp, 115)

    def test_initial_sleeping_state(self):
        """Test Lagavulin starts in sleeping state."""
        self.assertTrue(self.enemy_asc0.is_sleeping)
        self.assertFalse(self.enemy_asc0.is_stunned)

    def test_initial_intention_is_sleep(self):
        """Test initial intention is Sleep."""
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "sleep")

    def test_wakes_up_after_3_turns_without_damage(self):
        """Test Lagavulin wakes up after 3 turns without damage."""
        # Turn 1: Still sleeping
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "sleep")
        self.assertTrue(self.enemy_asc0.is_sleeping)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 1)

        # Turn 2: Still sleeping
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "sleep")
        self.assertTrue(self.enemy_asc0.is_sleeping)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 2)

        # Turn 3: Wakes up (counter reaches 3, shows attack intention)
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "attack")
        self.assertFalse(self.enemy_asc0.is_sleeping)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 3)

    def test_wakes_up_on_damage(self):
        """Test Lagavulin wakes up immediately when damaged."""
        # Verify initial state
        self.assertTrue(self.enemy_asc0.is_sleeping)
        self.assertFalse(self.enemy_asc0.is_stunned)

        # Take damage
        self.enemy_asc0.on_damage_taken(10)

        # Should wake up and become stunned
        self.assertFalse(self.enemy_asc0.is_sleeping)
        self.assertTrue(self.enemy_asc0.is_stunned)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 0)

    def test_stunned_intention_after_wake_on_damage(self):
        """Test intention is stunned after waking up from damage."""
        # Take damage while sleeping
        self.enemy_asc0.on_damage_taken(10)

        # Next intention should be stunned
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "stunned")

    def test_attack_pattern_after_wake(self):
        """Test attack pattern after waking up (Attack / Siphon Soul)."""
        # Wake up by taking damage
        self.enemy_asc0.on_damage_taken(10)
        self.enemy_asc0.is_stunned = False  # Clear stun for pattern testing

        # First action after wake: Attack
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "attack")
        self.enemy_asc0.current_intention = intention
        self.enemy_asc0.execute_intention()  # Toggle pattern

        # Second action: Siphon Soul
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "siphon_soul")
        self.enemy_asc0.current_intention = intention
        self.enemy_asc0.execute_intention()  # Toggle pattern

        # Third action: Attack
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "attack")
        self.enemy_asc0.current_intention = intention
        self.enemy_asc0.execute_intention()  # Toggle pattern

        # Fourth action: Siphon Soul
        intention = self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(intention.name, "siphon_soul")

    def test_dormant_to_active_state_transition(self):
        """Test dormant state changes to active state."""
        # Initially dormant (sleeping)
        self.assertTrue(self.enemy_asc0.is_sleeping)
        self.assertEqual(
            len([p for p in self.enemy_asc0.powers if p.name == "Metallicize"]), 1
        )

        # Wake up after 3 turns
        for _ in range(4):
            self.enemy_asc0.determine_next_intention(floor=1)

        # Now active (not sleeping, metallicize removed)
        self.assertFalse(self.enemy_asc0.is_sleeping)
        self.assertEqual(
            len([p for p in self.enemy_asc0.powers if p.name == "Metallicize"]), 0
        )

    def test_metallicize_removed_on_damage_wake(self):
        """Test Metallicize power is removed when waking up from damage."""
        # Verify Metallicize exists initially
        self.assertEqual(
            len([p for p in self.enemy_asc0.powers if p.name == "Metallicize"]), 1
        )

        # Take damage to wake up
        self.enemy_asc0.on_damage_taken(10)

        # Metallicize should be removed
        self.assertEqual(
            len([p for p in self.enemy_asc0.powers if p.name == "Metallicize"]), 0
        )

    def test_elite_flag(self):
        """Test Lagavulin is marked as Elite."""
        self.assertEqual(self.enemy_asc0.enemy_type, EnemyType.ELITE)
        self.assertEqual(self.enemy_asc3.enemy_type, EnemyType.ELITE)

    def test_execute_sleep_intention_does_nothing(self):
        """Test Sleep intention executes and returns no actions."""
        self.enemy_asc0.current_intention = self.enemy_asc0.intentions["sleep"]
        actions = self.enemy_asc0.execute_intention()
        self.assertEqual(actions, [])

    def test_execute_stunned_intention_does_nothing(self):
        """Test Stunned intention executes and returns no actions."""
        self.enemy_asc0.current_intention = self.enemy_asc0.intentions["stunned"]
        actions = self.enemy_asc0.execute_intention()
        self.assertEqual(actions, [])
        # Stun should be cleared
        self.assertFalse(self.enemy_asc0.is_stunned)

    def test_turns_without_damage_counter(self):
        """Test turns_without_damage counter increments correctly."""
        self.assertEqual(self.enemy_asc0.turns_without_damage, 0)

        # First turn
        self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 1)

        # Second turn
        self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 2)

        # Third turn
        self.enemy_asc0.determine_next_intention(floor=1)
        self.assertEqual(self.enemy_asc0.turns_without_damage, 3)


if __name__ == '__main__':
    unittest.main()
