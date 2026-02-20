"""Comprehensive tests for Heavy Blade card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.heavy_blade import HeavyBlade
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestHeavyBlade(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Heavy Blade has correct basic properties."""
        card = HeavyBlade()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.base_damage, 14)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)
        self.assertIn("strength_mult", card._magic)
        self.assertEqual(card._magic["strength_mult"], 3)

    def test_deals_damage(self):
        """Test Heavy Blade deals damage to enemy."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        self.assertLess(enemy.hp, 50)

    def test_upgraded(self):
        """Test upgraded Heavy Blade has more damage and multiplier."""
        card = HeavyBlade()
        card.upgrade()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card._magic["strength_mult"], 5)

    def test_energy_cost(self):
        """Test Heavy Blade costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)


if __name__ == '__main__':
    unittest.main()
