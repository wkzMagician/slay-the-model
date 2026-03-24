from types import SimpleNamespace

from actions.base import LambdaAction
from actions.display import InputRequestAction
from engine.game_state import GameState, game_state
from engine.input_protocol import InputRequest, InputSubmission
from engine.runtime_context import RuntimeContext
from localization import LocalStr
from utils.option import Option
from utils.result_types import NoneResult


def test_runtime_context_builds_message_participants_including_hand():
    hand = [object()]
    player_power = object()
    player_relic = object()
    enemy_power = object()
    enemy = SimpleNamespace(hp=10, powers=[enemy_power])
    player = SimpleNamespace(
        relics=[player_relic],
        powers=[player_power],
        card_manager=SimpleNamespace(
            get_pile=lambda pile_name: hand if pile_name == "hand" else []
        ),
    )

    ctx = RuntimeContext(player=player)

    assert ctx.message_participants(enemies=[enemy], include_hand=True) == [
        player,
        player_relic,
        player_power,
        enemy,
        enemy_power,
        hand[0],
    ]


def test_game_state_resolve_input_request_delegates_to_runtime_context():
    gs = GameState()
    expected = InputSubmission([])
    seen_requests = []

    class StubRuntimeContext:
        def resolve_input_request(self, request):
            seen_requests.append(request)
            return expected

    gs.runtime_context = StubRuntimeContext()
    request = InputRequest(
        options=[Option(name=LocalStr("ui.menu_return", default="Return"), actions=[])],
        max_select=1,
    )

    assert gs.resolve_input_request(request) is expected
    assert seen_requests == [request]


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
