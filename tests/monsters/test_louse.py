"""Test Louse enemies"""
import unittest
from enemies.act1.louse import RedLouse, GreenLouse
from tests.test_combat_utils import CombatTestHelper

class TestLouse(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_red_louse_hp(self):
        louse = RedLouse()
        self.assertGreaterEqual(louse.hp, 10)
        self.assertLessEqual(louse.hp, 15)

    def test_green_louse_hp(self):
        louse = GreenLouse()
        self.assertGreaterEqual(louse.hp, 11)
        self.assertLessEqual(louse.hp, 17)

if __name__ == '__main__':
    unittest.main()
