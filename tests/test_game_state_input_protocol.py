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


def test_human_selection_honors_game_state_helper_overrides(monkeypatch):
    gs = GameState()
    gs.config.mode = "manual"

    parsed_inputs = []

    def fake_augment(request):
        return [
            Option(
                name=LocalStr("ui.menu_return", default="Return"),
                actions=[LambdaAction(lambda: None)],
            )
        ]

    def fake_parse(raw_input, option_count, max_select, must_select):
        parsed_inputs.append((raw_input, option_count, max_select, must_select))
        return [0]

    gs._augment_human_options = fake_augment
    gs._parse_selection_input = fake_parse
    monkeypatch.setattr("builtins.input", lambda _prompt: "patched-input")

    submission = gs.resolve_input_request(
        InputRequest(
            options=[Option(name="ignored", actions=[LambdaAction(lambda: None)])],
            max_select=1,
        )
    )

    assert len(submission.actions) == 1
    assert parsed_inputs == [("patched-input", 1, 1, True)]


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
