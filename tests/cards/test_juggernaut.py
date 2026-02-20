"""Comprehensive tests for Juggernaut card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.juggernaut import Juggernaut
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestJuggernaut(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Juggernaut has correct basic properties."""
        card = Juggernaut()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertIn("damage_per_block", card._magic)
        self.assertEqual(card._magic["damage_per_block"], 5)

    def test_applies_power(self):
        """Test Juggernaut applies JuggernautPower."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Juggernaut()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Check that power was applied
        power_names = [type(p).__name__ for p in self.helper.game_state.player.powers]
        self.assertIn("JuggernautPower", power_names)

    def test_upgraded(self):
        """Test upgraded Juggernaut deals more damage."""
        card = Juggernaut()
        card.upgrade()
        self.assertEqual(card.cost, 2)  # Cost doesn't change
        self.assertEqual(card._magic["damage_per_block"], 7)

    def test_energy_cost(self):
        """Test Juggernaut costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Juggernaut()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == '__main__':
    unittest.main()
