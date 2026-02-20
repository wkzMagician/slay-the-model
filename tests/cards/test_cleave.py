"""
Test for Cleave card - Ironclad Attack card.

Cleave: Deal 8(11) damage to ALL enemies.
Cost: 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.cleave import Cleave
from enemies.act1.cultist import Cultist
from enemies.act1.jaw_worm import JawWorm


class TestCleave(unittest.TestCase):
    """Test cases for Cleave card."""

    def setUp(self):
        """Set up fresh combat for each test."""
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=80, max_hp=80, energy=3)

    def test_cleave_basic_properties(self):
        """Test basic card properties."""
        card = Cleave()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.base_damage, 8)
        self.assertFalse(card.exhaust)
        from utils.types import CardType
        self.assertEqual(card.card_type, CardType.ATTACK)

    def test_cleave_single_enemy(self):
        """Test that Cleave deals damage to single enemy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_enemy_hp = enemy.hp
        self.assertEqual(initial_enemy_hp, 50)

        card = Cleave()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Cleave")

        result = self.helper.play_card(card)
        self.assertTrue(result, "Cleave should be playable")

        self.helper.print_combat_state("After Cleave")

        # Check damage dealt (50 - 8 = 42)
        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 42, f"Enemy should take 8 damage, HP should be 42, got {final_enemy_hp}")

    def test_cleave_multiple_enemies(self):
        """Test that Cleave deals damage to ALL enemies."""
        enemy1 = self.helper.create_enemy(Cultist, hp=50)
        enemy2 = self.helper.create_enemy(JawWorm, hp=40)
        enemy3 = self.helper.create_enemy(Cultist, hp=30)
        combat = self.helper.start_combat([enemy1, enemy2, enemy3])

        # Record initial HP (may have changed during combat init)
        initial_hp = [enemy1.hp, enemy2.hp, enemy3.hp]

        card = Cleave()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Cleave")

        result = self.helper.play_card(card)
        self.assertTrue(result, "Cleave should be playable")

        self.helper.print_combat_state("After Cleave")

        # Check all enemies took damage (Cleave deals 8 damage to all)
        final_hp = [enemy1.hp, enemy2.hp, enemy3.hp]

        for i, (initial, final) in enumerate(zip(initial_hp, final_hp)):
            damage_taken = initial - final
            self.assertEqual(damage_taken, 8,
                           f"Enemy {i+1} should take 8 damage from Cleave, took {damage_taken}")

    def test_cleave_upgraded_damage(self):
        """Test upgraded Cleave deals more damage."""
        card = Cleave()
        card.upgrade()
        self.assertEqual(card.damage, 11)
        self.assertEqual(card.cost, 1)

        enemy1 = self.helper.create_enemy(Cultist, hp=50)
        enemy2 = self.helper.create_enemy(JawWorm, hp=40)
        combat = self.helper.start_combat([enemy1, enemy2])

        # Record initial HP (may have changed during combat init)
        initial_hp1, initial_hp2 = enemy1.hp, enemy2.hp

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card)
        self.assertTrue(result)

        # Check both enemies took 11 damage
        self.assertEqual(enemy1.hp, initial_hp1 - 11, "Upgraded Cleave should deal 11 damage to enemy 1")
        self.assertEqual(enemy2.hp, initial_hp2 - 11, "Upgraded Cleave should deal 11 damage to enemy 2")

    def test_cleave_energy_cost(self):
        """Test that Cleave costs 1 energy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_energy = self.helper.game_state.player.energy
        self.assertEqual(initial_energy, 3)

        card = Cleave()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card)

        # Energy should be 3 - 1 = 2
        final_energy = self.helper.game_state.player.energy
        self.assertEqual(final_energy, 2, "Cleave should cost 1 energy")

    def test_cleave_kills_multiple_enemies(self):
        """Test that Cleave can kill multiple enemies at once."""
        enemy1 = self.helper.create_enemy(Cultist, hp=8)
        enemy2 = self.helper.create_enemy(Cultist, hp=8)
        enemy3 = self.helper.create_enemy(Cultist, hp=8)
        combat = self.helper.start_combat([enemy1, enemy2, enemy3])

        card = Cleave()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card)
        self.assertTrue(result)

        # All enemies should be at 0 HP or below
        self.assertLessEqual(enemy1.hp, 0, "Enemy 1 should be killed")
        self.assertLessEqual(enemy2.hp, 0, "Enemy 2 should be killed")
        self.assertLessEqual(enemy3.hp, 0, "Enemy 3 should be killed")

    def test_cleave_no_targets(self):
        """Test Cleave behavior with no enemies."""
        # Start combat with empty enemy list
        combat = self.helper.start_combat([])

        card = Cleave()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card)
        # Cleave should still be playable even with no targets
        self.assertTrue(result, "Cleave should be playable with no enemies")


if __name__ == '__main__':
    unittest.main(verbosity=2)
