"""Selection must stay live when a fight has used every available move."""
from contextlib import contextmanager
import random
import sys

import pytest

from enemies.act3.awakened_one import AwakenedOne
from enemies.act3.time_eater import TimeEater
from tests.test_combat_utils import CombatTestHelper


@contextmanager
def bounded_selector():
    """Fail a regression deterministically instead of leaving pytest hung."""
    previous = sys.gettrace()
    lines = 0

    def trace(frame, event, arg):
        nonlocal lines
        if event == "line" and frame.f_code.co_name == "determine_next_intention":
            lines += 1
            if lines > 10000:
                raise AssertionError("Enemy selector stopped making progress")
        return trace

    sys.settrace(trace)
    try:
        yield
    finally:
        sys.settrace(previous)


@pytest.mark.parametrize("seed", [0, 1, 26, 20261026])
@pytest.mark.parametrize("phase", [1, 2])
def test_awakened_remains_live_after_mixed_history(seed, phase):
    helper = CombatTestHelper()
    random.seed(seed)
    enemy = AwakenedOne()
    enemy._phase = phase
    enemy.history_intentions = (
        ["Slash", "Slash", "Soul Strike"] if phase == 1
        else ["Rebirth", "Dark Echo", "Tackle", "Tackle", "Sludge", "Sludge"]
    )
    with bounded_selector():
        for _ in range(40):
            move = enemy._resolve_next_intention(enemy.determine_next_intention(1))
            assert move is not None
            name = move.name
            if phase == 1:
                assert name in {"Slash", "Soul Strike"}
                assert not (name == "Soul Strike" and enemy.history_intentions[-1] == name)
                assert not (name == "Slash" and enemy.history_intentions[-2:] == [name, name])
            else:
                assert name in {"Tackle", "Sludge"}
                assert enemy.history_intentions[-2:] != [name, name]
            enemy.history_intentions.append(name)
    helper._reset_game_state()


@pytest.mark.parametrize("seed", [0, 1, 26, 20261026])
def test_time_eater_remains_live_after_all_moves_used(seed):
    helper = CombatTestHelper()
    random.seed(seed)
    enemy = TimeEater()
    enemy.history_intentions = ["Reverberate", "Reverberate", "Head Slam", "Ripple"]
    with bounded_selector():
        for _ in range(40):
            move = enemy._resolve_next_intention(enemy.determine_next_intention(1))
            assert move is not None
            name = move.name
            assert name in {"Reverberate", "Head Slam", "Ripple"}
            if name == "Reverberate":
                assert enemy.history_intentions[-2:] != [name, name]
            else:
                assert enemy.history_intentions[-1] != name
            enemy.history_intentions.append(name)
    helper._reset_game_state()


def test_deca_high_ascension_protection_resolves_registered_power():
    from enemies.act3.deca import Deca
    from engine.combat import Combat

    helper = CombatTestHelper()
    helper.game_state.ascension = 19
    enemy = Deca()
    combat = Combat(enemies=[enemy])
    helper.game_state.combat = combat
    combat._init_combat()
    helper.game_state.drive_actions()
    enemy.current_intention = enemy.intentions["Square of Protection"]
    enemy.execute_intention()
    helper.game_state.drive_actions()
    assert any(type(power).__name__ == "PlatedArmorPower" for power in enemy.powers)
    helper._reset_game_state()
