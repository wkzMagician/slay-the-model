"""RUN-044: native exit must survive combat and room boundaries."""
import pytest

from actions.base import LambdaAction
from actions.display import MenuAction
from enemies.act1.gremlin_nob import GremlinNob
from engine.combat import Combat
from engine.game_flow import GameFlow
from engine.input_protocol import InputSubmission
from events.combat_event import CombatEvent
from rooms.combat import CombatRoom
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import RoomType


def environment():
    helper = create_test_helper()
    player = helper.create_player()
    player.base_draw_count = 0
    return helper.game_state, player, GremlinNob()


def exit_on_first_request(gs, monkeypatch):
    requests = []

    def choose(request):
        requests.append(request)
        assert len(requests) == 1, "Exit returned to another input request"
        return InputSubmission(actions=[LambdaAction(MenuAction(request)._exit_game)])

    monkeypatch.setattr(gs, "resolve_input_request", choose)
    return requests


def test_native_combat_exit_returns_once_without_enemy_action(monkeypatch):
    gs, player, enemy = environment()
    requests = exit_on_first_request(gs, monkeypatch)
    combat = Combat([enemy])
    assert combat.start() == GameTerminalState.GAME_EXIT
    assert len(requests) == 1
    assert player.hp == 80
    assert combat.combat_ended


@pytest.mark.parametrize("phase", ["player_start", "player_action", "player_end", "enemy_action"])
def test_each_phase_propagates_native_exit_before_next_action(phase, monkeypatch):
    gs, player, enemy = environment()
    combat = Combat([enemy])
    combat._init_combat()
    gs.drive_actions()
    combat.combat_state.current_phase = phase
    completed = []
    # Component contract: exit precedes pending phase work, using the real queue
    # and real menu command rather than replacing drive_actions or its result.
    gs.add_actions([
        LambdaAction(MenuAction(None)._exit_game),
        LambdaAction(lambda: completed.append("after exit")),
    ])
    if phase == "player_action":
        monkeypatch.setattr(gs, "resolve_input_request", lambda request: pytest.fail("Unexpected input"))
    assert combat._execute_next_phase() == GameTerminalState.GAME_EXIT
    assert completed == []
    assert player.hp == 80


@pytest.mark.parametrize("phase,checkpoint", [("player_end", 2), ("enemy_action", 2),
                                              ("enemy_action", 3), ("enemy_action", 4)])
def test_later_phase_checkpoints_stop_pending_actions(phase, checkpoint, monkeypatch):
    gs, player, enemy = environment()
    combat = Combat([enemy])
    combat._init_combat()
    gs.drive_actions()
    combat.combat_state.current_phase = phase
    native = gs.drive_actions
    calls = []
    completed = []

    def drive():
        calls.append(True)
        if len(calls) == checkpoint:
            gs.action_queue.add_actions([
                LambdaAction(MenuAction(None)._exit_game),
                LambdaAction(lambda: completed.append(True)),
            ], to_front=True)
        return native()

    monkeypatch.setattr(gs, "drive_actions", drive)
    assert combat._execute_next_phase() == GameTerminalState.GAME_EXIT
    assert len(calls) == checkpoint
    assert completed == []


def test_combat_opening_propagates_exit(monkeypatch):
    gs, player, enemy = environment()
    gs.add_action(LambdaAction(MenuAction(None)._exit_game))
    combat = Combat([enemy])
    assert combat.start() == GameTerminalState.GAME_EXIT
    assert combat.combat_ended
    assert player.hp == 80


@pytest.mark.parametrize("room_type", [RoomType.MONSTER, RoomType.ELITE, RoomType.BOSS])
def test_room_returns_exit_without_rewards(room_type, monkeypatch):
    gs, player, enemy = environment()
    requests = exit_on_first_request(gs, monkeypatch)
    room = CombatRoom([enemy], room_type=room_type)
    room.init()
    monkeypatch.setattr(room, "_handle_victory", lambda: pytest.fail("Exit granted victory"))
    gold = player.gold
    assert room.enter() == GameTerminalState.GAME_EXIT
    assert len(requests) == 1
    assert player.gold == gold
    assert gs.action_queue.is_empty()


def test_event_restores_exit_for_enclosing_action_driver(monkeypatch):
    gs, player, enemy = environment()
    exit_on_first_request(gs, monkeypatch)
    event = CombatEvent(enemies=[enemy])
    monkeypatch.setattr(event, "_handle_victory", lambda: pytest.fail("Exit granted event reward"))
    gs.add_action(LambdaAction(event.trigger))
    assert gs.drive_actions() == GameTerminalState.GAME_EXIT
    assert gs.action_queue.is_empty()
    assert player.hp == 80


def test_real_room_exit_finishes_outer_game_flow(monkeypatch):
    gs, player, enemy = environment()
    requests = exit_on_first_request(gs, monkeypatch)
    room = CombatRoom([enemy])
    flow = GameFlow()
    # Isolate map/Neo setup; the combat, room and outer loop stay native.
    def enter_first_room(state):
        flow.current_room = room
        flow.flow_phase = "enter_room"
    monkeypatch.setattr(flow, "_execute_init_act_phase", enter_first_room)
    exits = []
    native_exit = flow._handle_game_exit
    def handle_exit():
        exits.append(True)
        native_exit()
    monkeypatch.setattr(flow, "_handle_game_exit", handle_exit)
    flow.start_game(gs)
    assert flow.flow_phase == "finished"
    assert exits == [True]
    assert len(requests) == 1
    assert player.hp == 80
    assert gs.action_queue.is_empty()
