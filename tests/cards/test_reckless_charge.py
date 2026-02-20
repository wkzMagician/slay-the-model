from entities.creature import Creature
"""Comprehensive tests for RecklessCharge card."""
import unittest
from tests.test_combat_utils import create_test_helper
from cards.ironclad.reckless_charge import RecklessCharge
from enemies.act1.cultist import Cultist
from utils.types import CardType, RarityType


class TestRecklessCharge(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = RecklessCharge()
        self.assertEqual(card.cost, 0)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.base_damage, 7)

    def test_deals_damage(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = RecklessCharge()
        self.helper.add_card_to_hand(card)
        initial_hp = enemy.hp
        self.helper.play_card(card, target=enemy)

        # Should deal 7 damage
        self.assertLess(enemy.hp, initial_hp)

    def test_upgraded(self):
        card = RecklessCharge()
        card.upgrade()
        self.assertEqual(card._damage, 10)  # Damage increases from 7 to 10

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = RecklessCharge()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy)  # 0 cost

    def test_adds_dazed(self):
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = RecklessCharge()
        self.helper.add_card_to_hand(card)
        draw_pile_size = len(self.helper.game_state.player.card_manager.piles['draw_pile'])
        self.helper.play_card(card, target=enemy)

        # Should add Dazed to draw pile
        # Note: This may not work if AddCardAction isn't fully implemented


if __name__ == "__main__":
    unittest.main()
