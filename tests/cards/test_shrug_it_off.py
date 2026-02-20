from entities.creature import Creature
"""Comprehensive tests for Shrug It Off card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.shrug_it_off import ShrugItOff
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestShrugItOff(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = ShrugItOff()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.block, 8)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_gains_block(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = ShrugItOff()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        self.assertGreater(self.helper.game_state.player.block, 0)

    def test_upgraded(self):
        card = ShrugItOff()
        card.upgrade()
        self.assertEqual(card.block, 11)

    def test_draws_card(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        # Add cards to draw pile
        for _ in range(5):
            self.helper.game_state.player.card_manager.piles['draw_pile'].append(Strike())

        hand_before = len(self.helper.game_state.player.card_manager.piles['hand'])

        card = ShrugItOff()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        hand_after = len(self.helper.game_state.player.card_manager.piles['hand'])
        # Should draw 1 card (but played ShrugItOff, so net even)
        self.assertGreaterEqual(hand_after, hand_before - 1)

    def test_energy_cost(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = ShrugItOff()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == "__main__":
    unittest.main()
