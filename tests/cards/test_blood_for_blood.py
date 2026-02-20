from entities.creature import Creature
"""Comprehensive tests for Blood for Blood card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.blood_for_blood import BloodForBlood
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestBloodForBlood(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = BloodForBlood()
        self.assertEqual(card.cost, 4)
        self.assertEqual(card.damage, 18)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_deals_damage(self):
        player = self.helper.create_player(hp=80, energy=4)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = BloodForBlood()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        self.assertLess(enemy.hp, 50)

    def test_upgraded(self):
        card = BloodForBlood()
        card.upgrade()
        self.assertEqual(card.damage, 22)

    def test_energy_cost(self):
        player = self.helper.create_player(hp=80, energy=4)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = BloodForBlood()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 4)


if __name__ == "__main__":
    unittest.main()
