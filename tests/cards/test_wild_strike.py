from entities.creature import Creature
"""Test Wild Strike - Deals damage and adds Wound to draw pile"""
import unittest
from cards.ironclad.wild_strike import WildStrike
from tests.test_combat_utils import CombatTestHelper

class TestWildStrike(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_properties(self):
        card = WildStrike()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 12)

    def test_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = WildStrike()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 12)

    def test_upgraded(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        card = WildStrike()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, enemy)
        self.assertEqual(enemy.hp, 100 - 17)
        
    # todo: test shuffle card to draw

if __name__ == '__main__':
    unittest.main()
