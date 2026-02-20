"""Comprehensive tests for Whirlwind card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.whirlwind import Whirlwind
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestWhirlwind(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_basic_properties(self):
        """Test Whirlwind's basic properties."""
        card = Whirlwind()
        self.assertEqual(card.damage, 5)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
    
    def test_upgraded_properties(self):
        """Test Whirlwind+ has increased damage."""
        card = Whirlwind()
        card.upgrade()
        self.assertEqual(card.damage, 8)
    
    def test_energy_consumed(self):
        """Test Whirlwind consumes all current energy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        card = Whirlwind()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertEqual(self.player.energy, 0)
    
    def test_deals_damage_to_all_enemies(self):
        """Test Whirlwind damages all enemies."""
        self.player = self.helper.create_player(energy=2)
        enemy1 = self.helper.create_enemy(Cultist, hp=50)
        enemy2 = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy1, enemy2])
        
        initial_hp1 = enemy1.hp
        initial_hp2 = enemy2.hp
        
        card = Whirlwind()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy1)
        
        # Both enemies should take damage (5 damage * 2 attacks = 10 total each)
        self.assertLess(enemy1.hp, initial_hp1)
        self.assertLess(enemy2.hp, initial_hp2)


if __name__ == '__main__':
    unittest.main()
