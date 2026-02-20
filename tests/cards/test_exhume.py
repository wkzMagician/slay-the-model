from entities.creature import Creature
"""Comprehensive tests for Exhume card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.exhume import Exhume
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestExhume(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Exhume has correct basic properties."""
        card = Exhume()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertTrue(card.exhaust)  # Exhume exhausts itself

    def test_upgraded_properties(self):
        """Test upgraded Exhume has 0 cost."""
        card = Exhume()
        card.upgrade()
        self.assertEqual(card.cost, 0)  # Cost reduced to 0

    def test_returns_card_from_exhaust(self):
        """Test Exhume returns a card from exhaust pile."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        # Add a card to exhaust pile
        exhausted_card = Strike()
        self.helper.game_state.player.card_manager.piles['exhaust_pile'].append(exhausted_card)
        
        initial_exhaust = len(self.helper.game_state.player.card_manager.piles['exhaust_pile'])
        initial_hand = len(self.helper.game_state.player.card_manager.piles['hand'])
        
        card = Exhume()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Exhaust pile should decrease (or card moved)
        new_hand = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.assertGreater(new_hand, initial_hand)

    def test_energy_cost(self):
        """Test Exhume costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = Exhume()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)
        
        # Should consume 1 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
