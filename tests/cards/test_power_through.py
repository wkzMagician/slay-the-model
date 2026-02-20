"""Comprehensive tests for PowerThrough card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.power_through import PowerThrough
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestPowerThrough(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = PowerThrough()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.base_block, 15)

    def test_gains_block(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = PowerThrough()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Should gain 15 block
        self.assertGreater(self.helper.game_state.player.block, 0)

    def test_upgraded(self):
        card = PowerThrough()
        card.upgrade()
        self.assertEqual(card._block, 20)  # Block increases from 15 to 20

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = PowerThrough()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == "__main__":
    unittest.main()
