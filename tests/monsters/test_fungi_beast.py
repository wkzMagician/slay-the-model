"""Test Fungi Beast enemy"""
import unittest
from enemies.act1.fungi_beast import FungiBeast
from tests.test_combat_utils import CombatTestHelper

class TestFungiBeast(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_hp_range(self):
        beast = FungiBeast()
        self.assertGreaterEqual(beast.hp, 22)
        self.assertLessEqual(beast.hp, 28)

if __name__ == '__main__':
    unittest.main()
