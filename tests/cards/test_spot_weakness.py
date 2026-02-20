"""Comprehensive tests for Spot Weakness card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.spot_weakness import SpotWeakness
from enemies.act1.jaw_worm import JawWorm
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestSpotWeakness(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_basic_properties(self):
        """Test Spot Weakness's basic properties."""
        card = SpotWeakness()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
    
    def test_upgraded_properties(self):
        """Test Spot Weakness+ grants more strength."""
        card = SpotWeakness()
        card.upgrade()
        # Upgraded grants 4 strength instead of 3
        self.assertEqual(card.get_magic_value("strength"), 4)
    
    def test_energy_cost(self):
        """Test Spot Weakness costs 1 energy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_energy = self.player.energy
        
        card = SpotWeakness()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertEqual(self.player.energy, initial_energy - 1)
    
    def test_gains_strength_when_enemy_attacking(self):
        """Test gains strength when enemy intends to attack."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(JawWorm, hp=50)
        self.helper.start_combat([enemy])
        
        initial_strength = self.helper.get_power_stacks("Strength")
        
        card = SpotWeakness()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should gain 3 strength if enemy intends to attack
        final_strength = self.helper.get_power_stacks("Strength")
        self.assertGreater(final_strength, initial_strength)
        
        # todo: check not gain strength when enemy is not attacking


if __name__ == '__main__':
    unittest.main()
