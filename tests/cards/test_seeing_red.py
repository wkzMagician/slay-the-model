"""Comprehensive tests for Seeing Red card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.seeing_red import SeeingRed
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestSeeingRed(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Seeing Red has correct basic properties."""
        card = SeeingRed()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.base_energy_gain, 2)
        self.assertTrue(card.base_exhaust)

    def test_gains_energy(self):
        """Test Seeing Red gains 2 energy."""
        player = self.helper.create_player(energy=1, max_energy=5)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = SeeingRed()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        # Should gain 2 energy (net +1 after 1 cost)
        self.assertEqual(self.helper.game_state.player.energy, initial_energy + 1)

    def test_exhausts(self):
        """Test Seeing Red exhausts after play."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = SeeingRed()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Card should be in exhaust pile
        self.assertIn(card, player.card_manager.piles['exhaust_pile'])

    def test_upgraded(self):
        """Test upgraded Seeing Red costs 0."""
        card = SeeingRed()
        card.upgrade()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.upgrade_cost, 0)

    def test_energy_cost_upgraded(self):
        """Test upgraded Seeing Red costs 0 energy."""
        player = self.helper.create_player(energy=3, max_energy=5)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = SeeingRed()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        # Should gain 2 energy (net +2 after 0 cost)
        self.assertEqual(self.helper.game_state.player.energy, initial_energy + 2)


if __name__ == '__main__':
    unittest.main()
