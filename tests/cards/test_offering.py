from entities.creature import Creature
"""Comprehensive tests for Offering card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.offering import Offering
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestOffering(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Offering()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.RARE)
        self.assertEqual(card.base_heal, -6)  # Lose HP, not heal
        self.assertEqual(card.base_energy_gain, 2)
        self.assertEqual(card.base_draw, 3)
        self.assertTrue(card.exhaust)

    def test_upgraded(self):
        card = Offering()
        card.upgrade()
        self.assertEqual(card._heal, -6)  # HP loss doesn't change
        self.assertEqual(card._energy_gain, 2)  # Energy gain doesn't change
        self.assertEqual(card._draw, 5)  # Draw increases from 3 to 5

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3, max_energy=5)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Offering()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)

        # Net energy gain = +2 (0 cost + 2 gain)
        self.assertEqual(self.helper.game_state.player.energy, initial_energy + 2)

    def test_loses_hp(self):
        player = self.helper.create_player(hp=80)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        initial_hp = self.helper.game_state.player.hp
        card = Offering()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Should lose 6 HP
        self.assertEqual(self.helper.game_state.player.hp, initial_hp - 6)

    def test_gains_energy_when_starting_at_max(self):
        player = self.helper.create_player(energy=3, max_energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = Offering()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        # Offering should still grant +2 even when already at max energy.
        self.assertEqual(self.helper.game_state.player.energy, 5)


if __name__ == "__main__":
    unittest.main()
