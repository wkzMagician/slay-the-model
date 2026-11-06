from engine.random_streams import get_rng, StreamRandom
from typing import cast

from actions.display import DisplayTextAction, InputRequestAction
from events.wheel_of_change import WheelOfChange
from tests.test_combat_utils import create_test_helper


def test_wheel_of_change_wraps_gold_result_with_reveal_message(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    helper.game_state.current_act = 1
    helper.game_state.action_queue.clear()

    monkeypatch.setattr(get_rng("misc"), "choice", lambda items: items[0])

    event = WheelOfChange()
    event.trigger()

    menu = cast(InputRequestAction, helper.game_state.action_queue.queue[-1])
    assert isinstance(menu, InputRequestAction)
    assert isinstance(menu.options[0].actions[0], DisplayTextAction)
