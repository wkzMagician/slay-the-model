"""Test Slaver enemies"""
import unittest
from enemies.act1.slaver import RedSlaver, BlueSlaver
from tests.test_combat_utils import CombatTestHelper

class TestSlaver(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_red_slaver_hp(self):
        slaver = RedSlaver()
        self.assertGreaterEqual(slaver.hp, 46)
        self.assertLessEqual(slaver.hp, 50)

    def test_blue_slaver_hp(self):
        slaver = BlueSlaver()
        self.assertGreaterEqual(slaver.hp, 46)
        self.assertLessEqual(slaver.hp, 50)

if __name__ == '__main__':
    unittest.main()
