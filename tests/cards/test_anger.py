from entities.creature import Creature
"""
Test for Anger card - Ironclad Attack card.

Anger: Deal 6(8) damage. Add a copy of this card to your discard pile.
Cost: 0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.anger import Anger
from enemies.act1.cultist import Cultist


class TestAnger(unittest.TestCase):
    """Test cases for Anger card."""

    def setUp(self):
        """Set up fresh combat for each test."""
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=80, max_hp=80, energy=3)

    def test_anger_basic_properties(self):
        """Test basic card properties."""
        card = Anger()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.base_damage, 6)
        self.assertFalse(card.exhaust)
        from utils.types import CardType
        self.assertEqual(card.card_type, CardType.ATTACK)

    def test_anger_deals_damage(self):
        """Test that Anger deals correct damage."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_enemy_hp = enemy.hp
        self.assertEqual(initial_enemy_hp, 50)

        card = Anger()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Anger")

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result, "Anger should be playable")

        self.helper.print_combat_state("After Anger")

        # Check damage dealt (50 - 6 = 44)
        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 44, f"Enemy should take 6 damage, HP should be 44, got {final_enemy_hp}")

    def test_anger_adds_copy_to_discard(self):
        """Test that Anger adds a copy to discard pile when played."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Play Anger
        card = Anger()
        card_name = card.local("name")
        self.helper.add_card_to_hand(card)

        # Check discard pile before
        self.assertFalse(self.helper.is_card_in_discard(card_name),
                        "Anger should not be in discard before playing")

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        # Card should be in discard pile (played card + copy)
        # The played card goes to discard, and AddCardAction adds another copy
        discard_pile = self.helper.game_state.player.card_manager.piles['discard_pile']
        anger_count = sum(1 for c in discard_pile if c.local("name") == card_name or c.__class__.__name__ == "Anger")
        self.assertEqual(anger_count, 2, "Discard pile should have 2 Anger cards (played + copy)")

    def test_anger_upgraded_damage(self):
        """Test upgraded Anger deals more damage."""
        card = Anger()
        card.upgrade()
        self.assertEqual(card.damage, 8)
        self.assertEqual(card.cost, 0)

        # Test it deals 8 damage
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 42, "Upgraded Anger should deal 8 damage (50 - 8 = 42)")

    def test_anger_multiple_plays(self):
        """Test playing Anger multiple times accumulates copies."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Play Anger 3 times
        for i in range(3):
            card = Anger()
            self.helper.add_card_to_hand(card)
            self.helper.play_card(card, target=enemy)

        # Should have 6 Anger cards in discard (3 played + 3 copies)
        discard_pile = self.helper.game_state.player.card_manager.piles['discard_pile']
        anger_count = sum(1 for c in discard_pile if c.__class__.__name__ == "Anger")
        self.assertEqual(anger_count, 6, f"Discard should have 6 Anger cards after 3 plays, got {anger_count}")

    def test_anger_zero_cost(self):
        """Test that Anger costs 0 energy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_energy = self.helper.game_state.player.energy
        self.assertEqual(initial_energy, 3)

        card = Anger()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        # Energy should still be 3 (cost 0)
        final_energy = self.helper.game_state.player.energy
        self.assertEqual(final_energy, 3, "Energy should not change for cost 0 card")


if __name__ == '__main__':
    unittest.main(verbosity=2)
