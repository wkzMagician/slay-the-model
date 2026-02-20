from entities.creature import Creature
"""Comprehensive tests for Double Tap card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.double_tap import DoubleTap
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestDoubleTap(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DoubleTap()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertEqual(card.base_magic["double_card_num"], 1)

    def test_applies_power(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DoubleTap()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Check that DoubleTap power was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("DoubleTapPower", power_names)

    def test_upgraded_double_num(self):
        card = DoubleTap()
        card.upgrade()
        self.assertEqual(card._magic["double_card_num"], 2)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DoubleTap()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
