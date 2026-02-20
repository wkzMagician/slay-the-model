"""Comprehensive tests for Second Wind card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.second_wind import SecondWind
from cards.ironclad.defend import Defend
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestSecondWind(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Second Wind has correct basic properties."""
        card = SecondWind()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertIn("block_for_exhaust", card._magic)
        self.assertEqual(card._magic["block_for_exhaust"], 5)

    def test_exhausts_non_attacks(self):
        """Test Second Wind exhausts non-attack cards."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        # Add non-attack cards to hand
        for _ in range(2):
            player.card_manager.piles['hand'].append(Defend())

        initial_hand = len(player.card_manager.piles['hand'])
        initial_exhaust = len(player.card_manager.piles['exhaust_pile'])

        card = SecondWind()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Hand should have fewer cards (non-attacks exhausted)
        self.assertLess(len(player.card_manager.piles['hand']), initial_hand)

    def test_gains_block_per_exhaust(self):
        """Test Second Wind gains block for each exhausted card."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        # Add non-attack cards to hand
        for _ in range(2):
            player.card_manager.piles['hand'].append(Defend())

        initial_block = player.block

        card = SecondWind()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Should gain block (5 per exhaust * 2 cards = 10)
        self.assertGreater(player.block, initial_block)

    def test_upgraded(self):
        """Test upgraded Second Wind gains more block."""
        card = SecondWind()
        card.upgrade()
        self.assertEqual(card.cost, 1)  # Cost doesn't change
        self.assertEqual(card._magic["block_for_exhaust"], 7)

    def test_energy_cost(self):
        """Test Second Wind costs 1 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = SecondWind()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == '__main__':
    unittest.main()
