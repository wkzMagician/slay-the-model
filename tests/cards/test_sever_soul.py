from entities.creature import Creature
"""Comprehensive tests for Sever Soul card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.sever_soul import SeverSoul
from cards.ironclad.strike import Strike
from cards.ironclad.defend import Defend
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestSeverSoul(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()
    
    def test_basic_properties(self):
        """Test Sever Soul's basic properties."""
        card = SeverSoul()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 16)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
    
    def test_upgraded_properties(self):
        """Test Sever Soul+ has increased damage."""
        card = SeverSoul()
        card.upgrade()
        self.assertEqual(card.damage, 22)
    
    def test_energy_cost(self):
        """Test Sever Soul costs 2 energy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_energy = self.player.energy
        
        card = SeverSoul()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertEqual(self.player.energy, initial_energy - 2)
    
    def test_deals_damage(self):
        """Test Sever Soul deals damage to enemy."""
        self.player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        
        initial_hp = enemy.hp
        
        card = SeverSoul()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        self.assertLess(enemy.hp, initial_hp)
        
    # todo: test exhaust cards


if __name__ == '__main__':
    unittest.main()
