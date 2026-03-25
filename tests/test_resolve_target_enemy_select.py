"""Tests for resolve_target ENEMY_SELECT synchronous execution of SelectAction children."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from actions.base import LambdaAction
from actions.display import SelectAction
from engine.game_state import game_state
from utils.result_types import MultipleActionsResult
from utils.types import TargetType

from tests.test_combat_utils import CombatTestHelper


@pytest.mark.parametrize("chosen_idx", [0, 1])
def test_resolve_target_enemy_select_runs_lambda_actions(monkeypatch, chosen_idx):
    """MultipleActionsResult from SelectAction must be executed so last_select_idx applies."""
    helper = CombatTestHelper()
    from enemies.act1.cultist import Cultist

    enemies = [
        helper.create_enemy(Cultist, hp=10),
        helper.create_enemy(Cultist, hp=20),
    ]
    helper.start_combat(enemies)
    game_state.last_select_idx = -1

    def fake_execute(self):
        return MultipleActionsResult(
            [LambdaAction(func=lambda i=chosen_idx: setattr(game_state, "last_select_idx", i))]
        )

    # Two-arg dotted path splits at the last "." only, so "…SelectAction.execute"
    # wrongly resolves module "actions.display.SelectAction"; patch the class object.
    monkeypatch.setattr(SelectAction, "execute", fake_execute)

    from utils.combat import resolve_target

    targets = resolve_target(TargetType.ENEMY_SELECT)
    assert targets[0] is enemies[chosen_idx]
