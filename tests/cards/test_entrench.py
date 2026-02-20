"""Comprehensive test for Entrench - Double current block."""
import unittest
from cards.ironclad.entrench import Entrench
from cards.ironclad.defend import Defend
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestEntrench(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Entrench()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_upgraded_cost(self):
        card = Entrench()
        card.upgrade()
        self.assertEqual(card.cost, 0)

    def test_doubles_block(self):
        self.helper.create_player(max_hp=50)
        self.helper.start_combat([])
        # First gain 5 block with Defend
        defend = Defend()
        self.helper.add_card_to_hand(defend)
        self.helper.play_card(defend, None)
        # Then double with Entrench
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 5)
        card = Entrench()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        self.assertEqual(game_state.player.block, 10)

    def test_zero_energy_when_upgraded(self):
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        card = Entrench()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 3)

if __name__ == '__main__':
    unittest.main()
