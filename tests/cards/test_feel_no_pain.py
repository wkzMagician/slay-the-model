from entities.creature import Creature
"""Comprehensive tests for Feel No Pain card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.feel_no_pain import FeelNoPain
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestFeelNoPain(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Feel No Pain has correct basic properties."""
        card = FeelNoPain()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("block_per_exhaust", card._magic)
        self.assertEqual(card._magic["block_per_exhaust"], 3)

    def test_upgraded_properties(self):
        """Test upgraded Feel No Pain increases block per exhaust."""
        card = FeelNoPain()
        card.upgrade()
        self.assertEqual(card._magic["block_per_exhaust"], 4)

    def test_applies_power(self):
        """Test Feel No Pain applies power when played."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FeelNoPain()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should have the power applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertTrue(any("Feel" in name or "Exhaust" in name for name in power_names), 
                        f"Expected FeelNoPain power, got: {power_names}")

    def test_energy_cost(self):
        """Test Feel No Pain costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FeelNoPain()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)
        
        # Should consume 1 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
