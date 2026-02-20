from entities.creature import Creature
"""
Test for Pommel Strike card - Ironclad Attack card.

Pommel Strike: Deal 9(10) damage. Draw 1(2) card(s).
Cost: 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.pommel_strike import PommelStrike
from enemies.act1.cultist import Cultist
from enemies.act1.jaw_worm import JawWorm


class TestPommelStrike(unittest.TestCase):
    """Test cases for Pommel Strike card."""

    def setUp(self):
        """Set up fresh combat for each test."""
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=80, max_hp=80, energy=3)

    def test_pommel_strike_basic_properties(self):
        """Test basic card properties."""
        card = PommelStrike()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.base_damage, 9)
        self.assertFalse(card.exhaust)
        from utils.types import CardType
        self.assertEqual(card.card_type, CardType.ATTACK)

    def test_pommel_strike_deals_damage(self):
        """Test that Pommel Strike deals correct damage."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_enemy_hp = enemy.hp
        self.assertEqual(initial_enemy_hp, 50)

        card = PommelStrike()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Pommel Strike")

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result, "Pommel Strike should be playable")

        self.helper.print_combat_state("After Pommel Strike")

        # Check damage dealt (50 - 9 = 41)
        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 41, f"Enemy should take 9 damage, HP should be 41, got {final_enemy_hp}")

    def test_pommel_strike_draws_card(self):
        """Test that Pommel Strike draws 1 card."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Add some cards to draw pile
        from cards.ironclad.bash import Bash
        from cards.ironclad.cleave import Cleave
        self.helper.add_card_to_draw_pile(Bash())
        self.helper.add_card_to_draw_pile(Cleave())

        initial_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertEqual(initial_hand_size, 0, "Hand should start empty")

        card = PommelStrike()
        self.helper.add_card_to_hand(card)

        self.helper.print_combat_state("Before Pommel Strike")

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        self.helper.print_combat_state("After Pommel Strike")

        # Check that a card was drawn
        # Hand should have 1 card (the drawn card, since Pommel Strike was played)
        final_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertEqual(final_hand_size, 1, f"Pommel Strike should draw 1 card, hand size should be 1, got {final_hand_size}")

    def test_pommel_strike_upgraded_damage(self):
        """Test upgraded Pommel Strike deals more damage."""
        card = PommelStrike()
        card.upgrade()
        self.assertEqual(card.damage, 10)
        self.assertEqual(card.cost, 1)

        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        final_enemy_hp = enemy.hp
        self.assertEqual(final_enemy_hp, 40, "Upgraded Pommel Strike should deal 10 damage (50 - 10 = 40)")

    def test_pommel_strike_upgraded_draw(self):
        """Test upgraded Pommel Strike draws 2 cards."""
        card = PommelStrike()
        card.upgrade()

        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Add cards to draw pile
        from cards.ironclad.bash import Bash
        from cards.ironclad.cleave import Cleave
        from cards.ironclad.anger import Anger
        self.helper.add_card_to_draw_pile(Bash())
        self.helper.add_card_to_draw_pile(Cleave())
        self.helper.add_card_to_draw_pile(Anger())

        self.helper.add_card_to_hand(card)
        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        # Hand should have 2 cards (2 drawn)
        final_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertEqual(final_hand_size, 2, "Upgraded Pommel Strike should draw 2 cards")

    def test_pommel_strike_energy_cost(self):
        """Test that Pommel Strike costs 1 energy."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        initial_energy = self.helper.game_state.player.energy
        self.assertEqual(initial_energy, 3)

        card = PommelStrike()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        # Energy should be 3 - 1 = 2
        final_energy = self.helper.game_state.player.energy
        self.assertEqual(final_energy, 2, "Pommel Strike should cost 1 energy")

    def test_pommel_strike_draws_from_empty_pile(self):
        """Test Pommel Strike behavior when draw pile is empty."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Don't add any cards to draw pile - it's empty
        initial_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])

        card = PommelStrike()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result, "Pommel Strike should be playable even with empty draw pile")

        # Hand should be empty (no cards to draw)
        final_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertEqual(final_hand_size, 0, "Hand should remain empty when draw pile is empty")

    def test_pommel_strike_with_discard_pile(self):
        """Test that Pommel Strike draws from discard when draw pile is empty."""
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])

        # Add cards to discard pile
        from cards.ironclad.bash import Bash
        from cards.ironclad.cleave import Cleave
        self.helper.add_card_to_discard_pile(Bash())
        self.helper.add_card_to_discard_pile(Cleave())

        card = PommelStrike()
        self.helper.add_card_to_hand(card)

        result = self.helper.play_card(card, target=enemy)
        self.assertTrue(result)

        # Should have drawn 1 card (shuffle discard into draw, then draw)
        final_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertEqual(final_hand_size, 1, "Should draw 1 card from discard pile")


if __name__ == '__main__':
    unittest.main(verbosity=2)
