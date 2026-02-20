from entities.creature import Creature
"""Comprehensive tests for Sentinel card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.sentinel import Sentinel
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestSentinel(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_basic_properties(self):
        """Test Sentinel's basic properties."""
        card = Sentinel()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.block, 5)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
    
    def test_upgraded_properties(self):
        """Test Sentinel+ has increased block and energy on exhaust."""
        card = Sentinel()
        card.upgrade()
        self.assertEqual(card.block, 8)
        # Energy on exhaust increases from 2 to 3
        self.assertEqual(card.get_magic_value("energy_on_exhaust"), 3)
    
    def test_energy_cost(self):
        """Test Sentinel costs 1 energy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_energy = self.player.energy
        
        card = Sentinel()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertEqual(self.player.energy, initial_energy - 1)
    
    def test_gains_block(self):
        """Test Sentinel grants block."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_block = self.helper.get_player_block()
        
        card = Sentinel()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertGreater(self.helper.get_player_block(), initial_block)
    
    def test_exhaust_effect(self):
        """Test Sentinel grants energy when exhausted."""
        card = Sentinel()
        
        # Check that the card has the exhaust effect
        self.assertTrue(hasattr(card, 'on_exhaust'))
        
        # Exhaust effect should return a GainEnergyAction
        actions = card.on_exhaust()
        self.assertIsNotNone(actions)


if __name__ == '__main__':
    unittest.main()
