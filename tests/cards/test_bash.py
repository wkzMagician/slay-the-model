from entities.creature import Creature
"""
Test for Bash card - Ironclad Attack card.

Bash: Deal 8(10) damage. Apply 2(3) Vulnerable.
Cost: 2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.bash import Bash
from enemies.act1.cultist import Cultist


class TestBash(unittest.TestCase):
    """Test cases for Bash card."""

    def setUp(self):
        """Set up fresh combat for each test."""
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=80, max_hp=80, energy=3)

    def test_bash_basic_properties(self):
        """Test basic card properties."""
        card = Bash()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.base_damage, 8)
        self.assertFalse(card.exhaust)
        from utils.types import CardType
        self.assertEqual(card.card_type, CardType.ATTACK)

    def test_bash_deals_damage(self):
        """Test that Bash deals correct damage."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_enemy_hp = enemy.hp
        self.assertEqual(initial_enemy_hp, 50)

        card = Bash()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Bash")

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result, "Bash should be playable")

        self.helper.print_combat_state("After Bash")

        # Check damage dealt (50 - 8 = 42)
        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 42, f"Enemy should take 8 damage, HP should be 42, got {final_enemy_hp}")

    def test_bash_applies_vulnerable(self):
        """Test that Bash applies Vulnerable debuff to target."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Check enemy has no powers initially
        initial_powers = len(enemy.powers)
        self.assertEqual(initial_powers, 0, "Enemy should start with no powers")

        card = Bash()
        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        # Check enemy now has Vulnerable power
        self.assertGreater(len(enemy.powers), 0, "Enemy should have powers after Bash")

        # Find Vulnerable power
        vulnerable_power = None
        for power in enemy.powers:
            if "Vulnerable" in str(power.idstr):
                vulnerable_power = power
                break

        self.assertIsNotNone(vulnerable_power, "Enemy should have Vulnerable power")
        self.assertEqual(vulnerable_power.amount, 2, "Vulnerable should be 2 stacks")

    def test_bash_upgraded_damage(self):
        """Test upgraded Bash deals more damage."""
        card = Bash()
        card.upgrade()
        self.assertEqual(card.damage, 10)
        self.assertEqual(card.cost, 2)

        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 40, "Upgraded Bash should deal 10 damage (50 - 10 = 40)")

    def test_bash_upgraded_vulnerable(self):
        """Test upgraded Bash applies 3 Vulnerable."""
        card = Bash()
        card.upgrade()

        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        # Find Vulnerable power
        vulnerable_power = None
        for power in enemy.powers:
            if "Vulnerable" in str(power.idstr):
                vulnerable_power = power
                break

        self.assertIsNotNone(vulnerable_power, "Enemy should have Vulnerable power")
        self.assertEqual(vulnerable_power.amount, 3, "Upgraded Bash should apply 3 Vulnerable")

    def test_bash_energy_cost(self):
        """Test that Bash costs 2 energy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_energy = self.helper.game_state.player.energy
        self.assertEqual(initial_energy, 3)

        card = Bash()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        # Energy should be 3 - 2 = 1
        final_energy = self.helper.game_state.player.energy
        self.assertEqual(final_energy, 1, "Bash should cost 2 energy")

    def test_bash_insufficient_energy(self):
        """Test that Bash cannot be played without enough energy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Set energy to 1 (not enough for cost 2)
        self.helper.game_state.player.energy = 1

        card = Bash()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        self.assertFalse(result, "Bash should not be playable with insufficient energy")

        # Enemy HP should be unchanged
        self.assertEqual(enemy.hp, 50, "Enemy should not take damage")


if __name__ == '__main__':
    unittest.main(verbosity=2)
