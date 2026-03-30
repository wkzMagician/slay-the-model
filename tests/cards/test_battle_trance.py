from entities.creature import Creature
"""Comprehensive tests for BattleTrance card."""
import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.battle_trance import BattleTrance
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestBattleTrance(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test BattleTrance basic properties."""
        card = BattleTrance()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.damage, 0)
        self.assertEqual(card.base_draw, 3)

    def test_draws_cards(self):
        """Test that BattleTrance draws cards."""
        from cards.ironclad.strike import Strike
        
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Add cards to draw pile so draw has something to draw
        draw_pile = self.helper.game_state.player.card_manager.piles["draw_pile"]
        for _ in range(5):
            draw_pile.append(Strike())
        
        initial_hand_size = len(self.helper.game_state.player.card_manager.piles["hand"])
        card = BattleTrance()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Card should draw 3 cards
        new_hand_size = len(self.helper.game_state.player.card_manager.piles["hand"])
        self.assertGreaterEqual(new_hand_size, initial_hand_size + 2)  # At least 2 more (draw 3, -1 for playing)
        self.assertIsNotNone(self.helper.game_state.player.get_power("No Draw"))

    def test_upgraded(self):
        """Test upgraded BattleTrance draws more cards."""
        card = BattleTrance()
        card.upgrade()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.draw, 4)

    def test_energy_cost(self):
        """Test BattleTrance costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = BattleTrance()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == "__main__":
    unittest.main()
