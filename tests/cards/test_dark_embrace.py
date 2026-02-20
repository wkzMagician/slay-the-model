"""Comprehensive tests for Dark Embrace card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.dark_embrace import DarkEmbrace
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestDarkEmbrace(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DarkEmbrace()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.upgrade_cost, 1)

    def test_applies_power(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DarkEmbrace()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Check that DarkEmbrace power was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("DarkEmbracePower", power_names)

    def test_upgraded_cost(self):
        card = DarkEmbrace()
        card.upgrade()
        self.assertEqual(card.cost, 1)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DarkEmbrace()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == '__main__':
    unittest.main()
