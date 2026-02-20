"""Comprehensive tests for Carnage card."""
import unittest
from tests.test_combat_utils import CombatTestHelper, create_test_helper
from cards.ironclad.carnage import Carnage
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestCarnage(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Carnage basic properties."""
        card = Carnage()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 20)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertTrue(card.ethereal)

    def test_deals_damage(self):
        """Test that Carnage deals damage."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = Carnage()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=combat.enemies[0])
        
        # Should deal 20 damage
        self.assertLess(combat.enemies[0].hp, 50)

    def test_upgraded(self):
        """Test upgraded Carnage deals more damage."""
        card = Carnage()
        card.upgrade()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 28)

    def test_ethereal(self):
        """Test Carnage is ethereal."""
        card = Carnage()
        self.assertTrue(card.ethereal)

    def test_energy_cost(self):
        """Test Carnage costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        combat = self.helper.start_combat([enemy])
        
        card = Carnage()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=combat.enemies[0])
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == "__main__":
    unittest.main()
