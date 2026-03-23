import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import engine.game_state as game_state_module


@pytest.fixture(params=[1, 42, 100, 999, 12345, 666, 777, 8888])
def seed(request):
    return request.param


@pytest.fixture(autouse=True)
def reset_global_game_state():
    """Restore the real engine.game_state module and reset the singleton."""
    sys.modules["engine.game_state"] = game_state_module
    game_state_module.game_state.__init__()
    yield
    sys.modules["engine.game_state"] = game_state_module
    game_state_module.game_state.__init__()
