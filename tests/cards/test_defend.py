from entities.creature import Creature
"""
Comprehensive test suite for Defend card - Basic block.

Defend: Gain 5 (upgraded: 8) block. Cost 1 energy.
"""
import unittest
from cards.ironclad.defend import Defend
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType


class TestDefend(unittest.TestCase):
    """Test Defend card mechanics comprehensively"""

    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_defend_basic_properties(self):
        """Test Defend has correct basic properties"""
        card = Defend()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.block, 5)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.STARTER)

    def test_defend_gains_block(self):
        """Test Defend gains 5 block"""
        self.helper.create_player(max_hp=50)
        self.helper.start_combat([])
        
        card = Defend()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 5)

    def test_defend_energy_cost(self):
        """Test Defend costs 1 energy"""
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        
        card = Defend()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

    def test_defend_insufficient_energy(self):
        """Test Defend cannot be played with 0 energy"""
        self.helper.create_player(max_hp=50, energy=0)
        self.helper.start_combat([])
        
        card = Defend()
        self.helper.add_card_to_hand(card)
        
        can_play, reason = card.can_play()
        self.assertFalse(can_play)

    def test_defend_upgraded_block(self):
        """Test upgraded Defend gains 8 block"""
        self.helper.create_player(max_hp=50)
        self.helper.start_combat([])
        
        card = Defend()
        card.upgrade()
        self.assertEqual(card.block, 8)
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, None)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 8)

    def test_defend_multiple_in_deck(self):
        """Test playing multiple Defend cards stacks block"""
        self.helper.create_player(max_hp=50, energy=3)
        self.helper.start_combat([])
        
        for i in range(2):
            card = Defend()
            self.helper.add_card_to_hand(card)
            self.helper.play_card(card, None)
        
        # 5 * 2 = 10 block
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 10)

    def test_defend_no_target_needed(self):
        """Test Defend can be played without target"""
        self.helper.create_player(max_hp=50)
        self.helper.start_combat([])
        
        card = Defend()
        self.helper.add_card_to_hand(card)
        # Defend doesn't need a target
        self.helper.play_card(card, None)
        
        from engine.game_state import game_state
        self.assertEqual(game_state.player.block, 5)


if __name__ == '__main__':
    unittest.main()
