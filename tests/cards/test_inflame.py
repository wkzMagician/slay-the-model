from entities.creature import Creature
"""Comprehensive test suite for Inflame - Gain Strength."""
import unittest
from cards.ironclad.inflame import Inflame
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestInflame(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Inflame()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.get_magic_value("strength"), 2)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_gains_strength(self):
        self.helper.create_player(max_hp=50)
        self.helper.start_combat([])
        card = Inflame()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        stacks = self.helper.get_power_stacks("Strength")
        self.assertEqual(stacks, 2)

    def test_energy_cost(self):
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        card = Inflame()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

    def test_upgraded(self):
        card = Inflame()
        card.upgrade()
        self.assertEqual(card.get_magic_value("strength"), 3)

if __name__ == "__main__":
    unittest.main()
