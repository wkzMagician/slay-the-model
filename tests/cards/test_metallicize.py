"""Comprehensive tests for Metallicize card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.metallicize import Metallicize
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestMetallicize(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Metallicize()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("auto_block", card._magic)
        self.assertEqual(card._magic["auto_block"], 3)

    def test_upgraded(self):
        card = Metallicize()
        card.upgrade()
        self.assertEqual(card._magic["auto_block"], 4)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Metallicize()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)

    def test_is_power_card(self):
        card = Metallicize()
        self.assertEqual(card.card_type, CardType.POWER)


if __name__ == "__main__":
    unittest.main()
