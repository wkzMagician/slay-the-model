from entities.creature import Creature
"""Comprehensive tests for Fiend Fire card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.fiend_fire import FiendFire
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestFiendFire(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()
        
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Fiend Fire has correct basic properties."""
        card = FiendFire()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertIn("exhaust_damage", card._magic)
        self.assertEqual(card._magic["exhaust_damage"], 7)

    def test_upgraded_properties(self):
        """Test upgraded Fiend Fire increases exhaust damage."""
        card = FiendFire()
        card.upgrade()
        self.assertEqual(card._magic["exhaust_damage"], 10)

    def test_deals_damage(self):
        """Test Fiend Fire deals damage to enemy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        # Add cards to hand for exhausting
        for _ in range(3):
            self.helper.game_state.player.card_manager.piles['hand'].append(Strike())
        
        initial_hp = enemy.hp
        card = FiendFire()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)
        
        # Should deal damage
        self.assertLess(enemy.hp, initial_hp)

    def test_energy_cost(self):
        """Test Fiend Fire costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        combat = self.helper.start_combat([enemy])
        
        card = FiendFire()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)
        
        # Should consume 2 energy
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == '__main__':
    unittest.main()
