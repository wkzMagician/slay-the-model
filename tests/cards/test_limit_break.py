from entities.creature import Creature
"""
Test for Limit Break card - Ironclad Skill card.

Limit Break: Double your Strength. Exhaust.
Upgraded: Double your Strength. Exhaust.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.limit_break import LimitBreak
from powers.definitions.strength import StrengthPower
from enemies.act1.cultist import Cultist


class TestLimitBreak(unittest.TestCase):
    """Test cases for Limit Break card."""
    
    def setUp(self):
        """Set up fresh combat for each test."""
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=80, max_hp=80, energy=3)
        
    def test_limit_break_basic_properties(self):
        """Test basic card properties."""
        card = LimitBreak()
        self.assertEqual(card.cost, 1)
        self.assertTrue(card.exhaust)  # Card uses 'exhaust' property, not 'exhausts'
        # card_type is CardType enum, not string
        from utils.types import CardType
        self.assertEqual(card.card_type, CardType.SKILL)
        
    def test_limit_break_doubles_strength(self):
        """Test that Limit Break doubles current strength."""
        # Set up combat
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Add Strength power to player
        self.helper.add_power_to_player("Strength", amount=2)
        initial_strength = self.helper.get_power_stacks("Strength")
        self.assertEqual(initial_strength, 2, "Initial strength should be 2")
        
        # Add Limit Break to hand and play it
        card = LimitBreak()
        self.helper.add_card_to_hand(card)
        
        self.helper.print_combat_state("Before Limit Break")
        
        # Play the card
        result = self.helper.play_card(card)
        self.assertTrue(result, "Limit Break should be playable")
        
        self.helper.print_combat_state("After Limit Break")
        
        # Check strength is doubled
        new_strength = self.helper.get_power_stacks("Strength")
        self.assertEqual(new_strength, 4, f"Strength should be doubled from {initial_strength} to 4, got {new_strength}")
        
    def test_limit_break_with_zero_strength(self):
        """Test that Limit Break works even with zero strength."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Don't add any strength
        initial_strength = self.helper.get_power_stacks("Strength")
        self.assertEqual(initial_strength, 0, "Initial strength should be 0")
        
        # Play Limit Break
        card = LimitBreak()
        self.helper.add_card_to_hand(card)
        
        result = self.helper.play_card(card)
        self.assertTrue(result, "Limit Break should be playable even with 0 strength")
        
        # Strength should still be 0 (0 * 2 = 0)
        new_strength = self.helper.get_power_stacks("Strength")
        self.assertEqual(new_strength, 0, "Strength should remain 0")
        
    def test_limit_break_exhausts(self):
        """Test that Limit Break goes to exhaust pile after playing."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Add strength so the card has an effect
        self.helper.add_power_to_player("Strength", amount=3)
        
        # Play Limit Break
        card = LimitBreak()
        self.helper.add_card_to_hand(card)
        card_name = card.local("name")
        
        result = self.helper.play_card(card)
        self.assertTrue(result)
        
        # Card should NOT be in hand
        self.assertFalse(self.helper.is_card_in_hand(card_name), 
                        "Limit Break should not be in hand after playing")
        
        # Card should NOT be in discard pile (because it exhausts)
        self.assertFalse(self.helper.is_card_in_discard(card_name),
                        "Limit Break should not be in discard pile")
        
        # Card SHOULD be in exhaust pile
        self.assertTrue(self.helper.is_card_in_exhaust(card_name),
                       "Limit Break should be in exhaust pile")
        
    def test_limit_break_plus(self):
        """Test upgraded Limit Break has same behavior."""
        card = LimitBreak()
        card.upgrade()  # Upgrade the card
        self.assertEqual(card.cost, 1)
        self.assertFalse(card.exhaust)  # Upgraded Limit Break does NOT exhaust
        
        # Test it doubles strength
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        self.helper.add_power_to_player("Strength", amount=4)
        
        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card)
        self.assertTrue(result)
        
        new_strength = self.helper.get_power_stacks("Strength")
        self.assertEqual(new_strength, 8, "Upgraded Limit Break should also double strength")
        
    def test_limit_break_multiple_uses(self):
        """Test using Limit Break multiple times in same combat."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Start with 1 strength
        self.helper.add_power_to_player("Strength", amount=1)
        
        # First Limit Break
        card1 = LimitBreak()
        self.helper.add_card_to_hand(card1)
        self.helper.play_card(card1)
        self.assertEqual(self.helper.get_power_stacks("Strength"), 2)
        
        # Second Limit Break (need to draw a new one)
        card2 = LimitBreak()
        self.helper.add_card_to_hand(card2)
        self.helper.play_card(card2)
        self.assertEqual(self.helper.get_power_stacks("Strength"), 4)
        
        # Third Limit Break
        card3 = LimitBreak()
        self.helper.add_card_to_hand(card3)
        self.helper.play_card(card3)
        self.assertEqual(self.helper.get_power_stacks("Strength"), 8)


if __name__ == '__main__':
    unittest.main(verbosity=2)
