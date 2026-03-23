import unittest

from actions.combat import GainBlockAction
from tests.test_combat_utils import CombatTestHelper


class TestGainBlockActionCompat(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_accepts_legacy_amount_keyword(self):
        action = GainBlockAction(amount=6, target=self.player)
        result = action.execute()
        self.assertEqual(self.player.block, 6)


if __name__ == "__main__":
    unittest.main()
