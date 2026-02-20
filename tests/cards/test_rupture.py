from entities.creature import Creature
"""Comprehensive tests for Rupture card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.rupture import Rupture
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestRupture(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Rupture has correct basic properties."""
        card = Rupture()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("strength_gain", card._magic)
        self.assertEqual(card._magic["strength_gain"], 1)

    def test_applies_power(self):
        """Test Rupture applies RupturePower."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Rupture()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Check that power was applied
        power_names = [type(p).__name__ for p in self.helper.game_state.player.powers]
        self.assertIn("RupturePower", power_names)

    def test_upgraded(self):
        """Test upgraded Rupture gains more strength."""
        card = Rupture()
        card.upgrade()
        self.assertEqual(card.cost, 1)  # Cost doesn't change
        self.assertEqual(card._magic["strength_gain"], 2)

    def test_energy_cost(self):
        """Test Rupture costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Rupture()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
