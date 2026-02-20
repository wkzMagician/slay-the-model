from entities.creature import Creature
"""Comprehensive test suite for Demon Form - Gain Strength each turn."""
import unittest
from cards.ironclad.demon_form import DemonForm
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestDemonForm(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DemonForm()
        self.assertEqual(card.cost, 3)
        self.assertEqual(card.get_magic_value("strength_per_turn"), 2)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.RARE)

    def test_energy_cost(self):
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        card = DemonForm()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 0)

    def test_upgraded_strength(self):
        card = DemonForm()
        card.upgrade()
        self.assertEqual(card.get_magic_value("strength_per_turn"), 3)

if __name__ == '__main__':
    unittest.main()
