"""Test Slime Boss enemy"""
import unittest
from enemies.act1.slime_boss import SlimeBoss
from tests.test_combat_utils import CombatTestHelper
from utils.types import EnemyType

class TestSlimeBoss(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_hp_range(self):
        boss = SlimeBoss()
        self.assertGreaterEqual(boss.hp, 140)
        self.assertLessEqual(boss.hp, 144)
        
    def test_is_boss(self):
        boss = SlimeBoss()
        self.assertEqual(boss.enemy_type, EnemyType.BOSS)

if __name__ == '__main__':
    unittest.main()
