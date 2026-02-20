from entities.creature import Creature
"""Comprehensive tests for Combust card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.combust import Combust
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestCombust(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Combust()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.base_magic["combust_damage"], 5)

    def test_applies_power(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Combust()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Check that Combust power was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("CombustPower", power_names)

    def test_upgraded_damage(self):
        card = Combust()
        card.upgrade()
        self.assertEqual(card._magic["combust_damage"], 7)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Combust()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
