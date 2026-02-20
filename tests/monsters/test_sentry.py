"""Test Sentry elite enemy"""
import unittest
from enemies.act1.sentry import Sentry
from tests.test_combat_utils import CombatTestHelper
from utils.types import EnemyType

class TestSentry(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_hp_range(self):
        sentry = Sentry()
        self.assertGreaterEqual(sentry.hp, 38)
        self.assertLessEqual(sentry.hp, 42)
        
    def test_is_elite(self):
        sentry = Sentry()
        self.assertEqual(sentry.enemy_type, EnemyType.ELITE)

if __name__ == '__main__':
    unittest.main()
