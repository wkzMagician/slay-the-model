"""Comprehensive tests for War Cry card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.war_cry import WarCry
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestWarCry(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_basic_properties(self):
        """Test War Cry's basic properties."""
        card = WarCry()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.COMMON)
    
    def test_upgraded_properties(self):
        """Test War Cry+ draws more cards."""
        card = WarCry()
        card.upgrade()
        # Upgraded draws 2 cards instead of 1
        self.assertEqual(card.draw, 2)
    
    def test_zero_energy_cost(self):
        """Test War Cry costs 0 energy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_energy = self.player.energy
        
        card = WarCry()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # War Cry costs 0 energy
        self.assertEqual(self.player.energy, initial_energy)
        
    # todo: test draw card and move card to draw


if __name__ == '__main__':
    unittest.main()
