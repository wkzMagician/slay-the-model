"""Test Jaw Worm enemy"""
import unittest
from enemies.act1.jaw_worm import JawWorm
from tests.test_combat_utils import CombatTestHelper

class TestJawWorm(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_hp_range(self):
        worm = JawWorm()
        self.assertGreaterEqual(worm.hp, 40)
        self.assertLessEqual(worm.hp, 50)

if __name__ == '__main__':
    unittest.main()
