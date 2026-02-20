from entities.creature import Creature
"""Test Twin Strike card mechanics"""
import unittest
from cards.ironclad.twin_strike import TwinStrike
from tests.test_combat_utils import CombatTestHelper

class TestTwinStrike(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_twin_strike_properties(self):
        card = TwinStrike()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.damage, 5)
        self.assertEqual(card.attack_times, 2)

    def test_twin_strike_damage(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        twin_strike = TwinStrike()
        self.helper.add_card_to_hand(twin_strike)
        self.helper.play_card(twin_strike, enemy)
        self.assertEqual(enemy.hp, 100 - 10)  # 5 * 2

    def test_twin_strike_upgraded(self):
        from enemies.act1.cultist import Cultist
        self.helper.create_player(max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=100)
        self.helper.start_combat([enemy])
        twin_strike = TwinStrike()
        twin_strike.upgrade()
        self.helper.add_card_to_hand(twin_strike)
        self.helper.play_card(twin_strike, enemy)
        self.assertEqual(enemy.hp, 100 - 14)  # 7 * 2

if __name__ == '__main__':
    unittest.main()
