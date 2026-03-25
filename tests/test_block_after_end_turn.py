"""Regression: player block must survive end of player turn until enemy attacks resolve."""

import unittest

from actions.combat import AttackAction
from enemies.act1.cultist import Cultist
from engine.game_state import game_state
from tests.test_combat_utils import CombatTestHelper


class TestBlockAfterEndTurn(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_block_persists_after_end_player_phase_and_absorbs_attack(self):
        self.helper.create_player(hp=50, max_hp=50)
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])

        game_state.player.block = 20
        hp_before = game_state.player.hp

        self.helper.end_player_turn()

        self.assertEqual(
            game_state.player.block,
            20,
            "block should not be cleared before enemy turn",
        )

        self.helper._execute_actions_recursive(
            [
                AttackAction(
                    damage=6,
                    target=game_state.player,
                    source=enemy,
                    damage_type="attack",
                )
            ]
        )

        self.assertEqual(game_state.player.hp, hp_before)
        self.assertEqual(game_state.player.block, 14)


if __name__ == "__main__":
    unittest.main()
