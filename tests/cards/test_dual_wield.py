"""Comprehensive tests for Dual Wield card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.dual_wield import DualWield
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestDualWield(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DualWield()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.upgrade_cost, 0)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DualWield()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)

    def test_upgraded_cost(self):
        card = DualWield()
        card.upgrade()
        self.assertEqual(card.cost, 0)


if __name__ == '__main__':
    unittest.main()
