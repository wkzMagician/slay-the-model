"""Test Gremlin Nob elite enemy"""
import unittest
from enemies.act1.gremlin_nob import GremlinNob
from tests.test_combat_utils import CombatTestHelper
from utils.types import EnemyType

class TestGremlinNob(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
    def tearDown(self):
        self.helper._reset_game_state()

    def test_hp_range(self):
        nob = GremlinNob()
        self.assertGreaterEqual(nob.hp, 82)
        self.assertLessEqual(nob.hp, 87)
        
    def test_is_elite(self):
        nob = GremlinNob()
        self.assertEqual(nob.enemy_type, EnemyType.ELITE)

if __name__ == '__main__':
    unittest.main()
