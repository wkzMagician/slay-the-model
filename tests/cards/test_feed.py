from entities.creature import Creature
"""Comprehensive test suite for Feed - Gain Max HP on fatal."""
import unittest
from cards.ironclad.feed import Feed
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestFeed(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Feed()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 10)
        self.assertEqual(card.get_magic_value("max_health_gain"), 3)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.RARE)

    def test_deals_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Feed()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 10)

    def test_upgraded_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Feed()
        card.upgrade()
        self.assertEqual(card.damage, 12)
        self.assertEqual(card.get_magic_value("max_health_gain"), 4)
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 12)

    def test_energy_cost(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Feed()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        from engine.game_state import game_state
        self.assertEqual(game_state.player.energy, 2)

if __name__ == '__main__':
    unittest.main()
