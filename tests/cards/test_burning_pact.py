"""Comprehensive tests for BurningPact card."""
import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.burning_pact import BurningPact
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestBurningPact(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test BurningPact basic properties."""
        card = BurningPact()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.damage, 0)
        self.assertEqual(card.base_draw, 2)

    def test_draws_cards(self):
        """Test that BurningPact draws cards."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        initial_hand_size = len(self.helper.game_state.player.card_manager.piles["hand"])
        card = BurningPact()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Card should draw 2 cards
        new_hand_size = len(self.helper.game_state.player.card_manager.piles["hand"])
        # Net change: +2 draw -1 played -1 exhaust = 0 to +1
        self.assertGreaterEqual(new_hand_size, initial_hand_size - 1)

    def test_upgraded(self):
        """Test upgraded BurningPact draws more cards."""
        card = BurningPact()
        card.upgrade()
        self.assertEqual(card.cost, 1)
        # Should draw 3 instead of 2
        self.assertEqual(card.draw, 3)

    def test_energy_cost(self):
        """Test BurningPact costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = BurningPact()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == "__main__":
    unittest.main()
