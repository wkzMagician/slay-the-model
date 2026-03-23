from actions.base import LambdaAction
from actions.display import InputRequestAction
from engine.game_state import game_state
from localization import LocalStr
from utils.option import Option
from utils.result_types import NoneResult


def test_drive_actions_resolves_input_request_in_debug_mode():
    executed = []

    game_state.config.mode = "debug"
    game_state.config.debug["select_type"] = "first"

    game_state.action_queue.add_action(
        InputRequestAction(
            title=LocalStr("ui.choose_blessings"),
            options=[
                Option(
                    name=LocalStr("ui.menu_return", default="Return"),
                    actions=[LambdaAction(lambda: executed.append("picked"))],
                )
            ],
        )
    )

    result = game_state.drive_actions()

    assert isinstance(result, NoneResult)
    assert executed == ["picked"]
    assert game_state.action_queue.is_empty()
