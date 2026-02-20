from entities.creature import Creature
"""Comprehensive tests for Pummel card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.pummel import Pummel
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestPummel(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Pummel()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 2)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_deals_damage(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = Pummel()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        # Pummel hits 4 times for 2 damage each = 8 damage
        self.assertLessEqual(enemy.hp, 42)

    def test_upgraded(self):
        card = Pummel()
        card.upgrade()
        self.assertEqual(card.damage, 2)
        # Upgrade increases attack_times to 5

    def test_energy_cost(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = Pummel()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)


if __name__ == "__main__":
    unittest.main()
