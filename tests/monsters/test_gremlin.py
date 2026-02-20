"""Test Gremlin enemies"""
import unittest
from enemies.act1.gremlin import FatGremlin, SneakyGremlin, MadGremlin
from tests.test_combat_utils import CombatTestHelper

class TestGremlin(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_fat_gremlin_hp(self):
        gremlin = FatGremlin()
        self.assertGreaterEqual(gremlin.hp, 10)
        self.assertLessEqual(gremlin.hp, 20)

    def test_sneaky_gremlin_hp(self):
        gremlin = SneakyGremlin()
        self.assertGreaterEqual(gremlin.hp, 8)
        self.assertLessEqual(gremlin.hp, 15)

    def test_mad_gremlin_hp(self):
        gremlin = MadGremlin()
        self.assertGreaterEqual(gremlin.hp, 8)
        self.assertLessEqual(gremlin.hp, 15)

if __name__ == '__main__':
    unittest.main()
