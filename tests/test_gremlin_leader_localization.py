import unittest

from engine.game_state import game_state
from enemies.act2.gremlin_leader import GremlinLeader
from tests.test_combat_utils import CombatTestHelper


class TestGremlinLeaderLocalization(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
        self.helper.create_player()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_current_intention_description_is_localized(self):
        enemy = GremlinLeader()
        for intention in enemy.intentions.values():
            description = str(intention.description)
            self.assertFalse(description.startswith("enemies.GremlinLeader.intentions."))


if __name__ == "__main__":
    unittest.main()
