"""Comprehensive test suite for Flex - Temporary Strength."""
import unittest
from cards.ironclad.flex import Flex
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestFlex(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Flex()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.get_magic_value("temp_strength"), 2)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_zero_energy_cost(self):
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        card = Flex()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 3)

    def test_upgraded(self):
        card = Flex()
        card.upgrade()
        self.assertEqual(card.get_magic_value("temp_strength"), 4)
        
    # todo: test apply power

if __name__ == "__main__":
    unittest.main()
