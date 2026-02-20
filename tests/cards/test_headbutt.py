"""Comprehensive test for Headbutt - Damage and return card"""
import unittest
from cards.ironclad.headbutt import Headbutt
from tests.test_combat_utils import CombatTestHelper
from utils.types import CardType, RarityType

class TestHeadbutt(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Headbutt()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 9)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)

    def test_deals_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Headbutt()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 9)

    def test_upgraded_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = Headbutt()
        card.upgrade()
        self.assertEqual(card.damage, 12)
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 12)
        
    # todo: test move card from discard to top of draw

if __name__ == '__main__':
    unittest.main()
