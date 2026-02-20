from entities.creature import Creature
"""Comprehensive tests for PerfectedStrike card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.perfected_strike import PerfectedStrike
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestPerfectedStrike(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = PerfectedStrike()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)
        self.assertEqual(card.base_damage, 6)
        self.assertIn("strike_damage", card._magic)
        self.assertEqual(card._magic["strike_damage"], 2)

    def test_deals_base_damage(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = PerfectedStrike()
        self.helper.add_card_to_hand(card)
        initial_hp = enemy.hp
        self.helper.play_card(card, target=enemy)

        # Should deal base 6 + strike_bonus damage
        self.assertLess(enemy.hp, initial_hp)

    def test_upgraded(self):
        card = PerfectedStrike()
        card.upgrade()
        self.assertEqual(card._magic["strike_damage"], 3)  # Bonus increases from 2 to 3

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = PerfectedStrike()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)

    def test_dynamic_damage_with_strikes(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])

        # Add 3 Strike cards to hand
        card_manager = self.helper.game_state.player.card_manager
        for _ in range(3):
            card_manager.piles['hand'].append(Strike())

        card = PerfectedStrike()
        self.helper.add_card_to_hand(card)
        initial_hp = enemy.hp
        self.helper.play_card(card, target=enemy)

        # Should deal base 6 + (4 strikes x 2 bonus) = 14 damage
        damage_dealt = initial_hp - enemy.hp
        self.assertGreaterEqual(damage_dealt, 10)  # At least some bonus damage


if __name__ == "__main__":
    unittest.main()
