"""Approved runtime blockers: actual map/room flow, event combat and save IO."""
import os
import pickle
import pickletools
import random
from typing import cast

import pytest

from actions.combat import EndTurnAction, PlayCardAction, StartFightAction, UsePotionAction
from actions.display import InputRequestAction, MenuAction
from engine.combat import Combat
from engine.game_flow import GameFlow
from engine.input_protocol import InputRequest
from engine.game_state import game_state as state
from events.dead_adventurer import DeadAdventurer
from events.hypnotizing_mushrooms import HypnotizingColoredMushrooms
from events.the_colosseum import TheColosseum
from map.encounter_pool import EncounterPool
from map.map_manager import MapManager
from potions.global_potions import SmokeBomb
from relics.global_relics.event import OddMushroom
from relics.global_relics.special import BlueKey, RedKey, GreenKey
from rooms.combat import CombatRoom
from rooms.event import EventRoom
from rooms.victory import VictoryRoom
from utils.result_types import GameTerminalState
from utils.types import CardType, RoomType


@pytest.mark.parametrize('act,ascension,floors', [
    (1, 0, [16]), (2, 20, [16]), (3, 0, [16]),
    (3, 20, [16, 17]), (4, 0, [3]), (4, 20, [3]),
])
def test_real_map_boss_nodes_produce_live_encounters(act, ascension, floors):
    state.current_act = act
    state.ascension = ascension
    manager = MapManager(seed=42, act_id=act)
    data = manager.generate_map()
    previous = next(n for n in data.nodes[floors[0] - 1] if 0 in n.connections_up)
    data.set_current_position(previous.floor - manager._get_act_start_floor(act), previous.position)
    names = []
    for floor in floors:
        created_room = manager.move_to_node(manager._get_act_start_floor(act) + floor, 0)
        assert isinstance(created_room, CombatRoom)
        room = cast(CombatRoom, created_room)
        assert room.enemies and all(e.hp > 0 for e in room.enemies)
        assert room.encounter_name
        room.init()
        assert room.combat is not None
        assert room.combat._check_combat_end() != GameTerminalState.COMBAT_WIN
        names.append(room.encounter_name)
    assert len(names) == len(set(names))


def test_empty_boss_is_rejected_before_combat_can_award_victory():
    room = CombatRoom(enemies=[], room_type=RoomType.BOSS)
    before = (state.player.hp, state.player.gold)
    with pytest.raises(ValueError, match='nonempty encounter'):
        room.init()
    assert room.combat is None
    assert before == (state.player.hp, state.player.gold)


@pytest.mark.parametrize('ascension', [0, 5, 19, 20])
def test_keyed_victory_room_advances_flow_and_heals_once(ascension):
    state.ascension = ascension
    state.current_act = 4  # MoveToMapNodeAction already identifies destination act.
    state.player.max_hp = 80
    state.player.hp = 40
    state.player.relics.extend([RedKey(), GreenKey(), BlueKey()])
    room = VictoryRoom()
    state.current_room = room
    flow = GameFlow()
    flow.current_room = room
    flow.flow_phase = 'enter_room'
    assert flow._execute_enter_room_phase(state) is None
    assert flow.flow_phase == 'complete_act'
    assert state.player.hp == 40
    assert flow._execute_complete_act_phase(state) is None
    assert flow.flow_phase == 'init_act'
    assert state.player.hp == (80 if ascension < 5 else 70)
    healed = state.player.hp
    flow._execute_init_act_phase(state)
    assert state.map_manager.act_id == 4
    assert state.player.hp == healed


@pytest.mark.parametrize('act', [4, 5])
def test_victory_without_keys_or_after_heart_remains_terminal(act):
    state.current_act = act
    state.player.relics.clear()
    assert VictoryRoom().enter() == GameTerminalState.GAME_WIN


def test_real_exhausted_event_pool_advances_to_room_selection():
    import events  # noqa: F401
    from events.event_pool import event_pool
    # Use the actual consume API, not a replacement empty provider.
    for ident in event_pool.get_all_registered_events():
        event_pool.mark_event_used(ident)
    room = EventRoom()
    state.current_room = room
    flow = GameFlow()
    flow.current_room = room
    flow.flow_phase = 'enter_room'
    assert flow._execute_enter_room_phase(state) is None
    assert flow.flow_phase == 'select_room'
    assert flow.current_room is None
    assert state.action_queue.is_empty()


@pytest.mark.parametrize('ascension', [0, 15])
@pytest.mark.parametrize('mode', ['mushroom_win', 'mushroom_escape', 'dead_escape',
                                  'colosseum_first_escape', 'colosseum_second_escape'])
def test_native_event_fight_and_smoke_bomb_finish_room(monkeypatch, ascension, mode):
    state.ascension = ascension
    state.config.auto_select = False
    state.config.debug['select_type'] = 'first'
    random.seed(42)
    state.player.potions.clear()
    if mode.startswith('mushroom'):
        event = HypnotizingColoredMushrooms()
    elif mode == 'dead_escape':
        event = DeadAdventurer()
        # Isolate the encounter branch; enemies, combat and potion remain real.
        monkeypatch.setattr(event, '_get_elite_chance', lambda: 100)
    else:
        event = TheColosseum()
    if mode != 'mushroom_win':
        state.player.potions.append(SmokeBomb())
    room = EventRoom()
    room.selected_event = event
    room.available_events = [event]
    state.current_room = room
    combats = []
    initial_enemies = []
    requests = []
    before = (state.player.gold, len(state.player.deck), len(state.player.relics))

    def choose(req):
        requests.append(req)
        assert len(requests) < 90
        combat = state.current_combat
        if combat is not None and not combat.combat_ended:
            if combat not in combats:
                combats.append(combat)
                initial_enemies.append([type(e).__name__ for e in combat.enemies])
                win = mode == 'mushroom_win' or (
                    mode == 'colosseum_second_escape' and len(combats) == 1)
                if win:
                    for enemy in combat.enemies:
                        enemy.hp = 1  # Native attack/win path; not a fake combat result.
            escape = mode != 'mushroom_win' and not (
                mode == 'colosseum_second_escape' and len(combats) == 1)
            index = next((i for i, option in enumerate(req.options) if option.enabled and any(
                isinstance(a, UsePotionAction) if escape else
                isinstance(a, PlayCardAction) and a.card.card_type == CardType.ATTACK
                for a in option.actions)), None)
            if index is None:
                index = next((i for i, o in enumerate(req.options)
                              if any(isinstance(a, EndTurnAction) for a in o.actions)), None)
            if index is None:
                index = next(i for i, o in enumerate(req.options) if o.enabled)
        else:
            index = 0
        return state._build_submission(req.options, [index])

    monkeypatch.setattr(state, 'resolve_input_request', choose)
    room.enter()
    assert state.drive_actions() is None
    room._sync_leave_state()
    assert event.event_ended and room.should_leave
    assert len(combats) == (2 if mode == 'colosseum_second_escape' else 1)
    if mode.startswith('mushroom'):
        assert initial_enemies[0] == ['FungiBeast'] * 3
    if mode == 'mushroom_win':
        assert sum(isinstance(r, OddMushroom) for r in state.player.relics) == 1
    else:
        assert not state.player.potions
        assert before == (state.player.gold, len(state.player.deck), len(state.player.relics))
        assert all(e.hp > 0 for e in combats[-1].enemies)
        if isinstance(event, TheColosseum):
            assert event.first_fight_done == (mode == 'colosseum_second_escape')


@pytest.mark.parametrize('act', [1, 2, 3, 4])
def test_encounter_pool_roundtrip_preserves_rng_and_factory_tables(act):
    pool = EncounterPool(seed=42, act_id=act)
    pool.get_elite_encounter(floor=8)
    restored = pickle.loads(pickle.dumps(pool))
    assert restored.rng.getstate() == pool.rng.getstate()
    assert restored.easy_pool == pool.easy_pool
    assert restored.hard_pool == pool.hard_pool
    assert restored.elite_pool == pool.elite_pool
    assert restored.boss_pool == pool.boss_pool
    assert restored.get_boss_encounter(floor=3 if act == 4 else 16)[1] == pool.get_boss_encounter(floor=3 if act == 4 else 16)[1]
    for factory, _ in restored.easy_pool.values():
        assert factory()


def save_fixture_path(monkeypatch, tmp_path):
    import actions.display as display
    actions_dir = tmp_path / 'actions'
    actions_dir.mkdir()
    monkeypatch.setattr(display, '__file__', str(actions_dir / 'display.py'))
    return tmp_path / 'savegame.pkl'


@pytest.mark.parametrize('act', [1, 2, 3, 4])
def test_native_save_writes_complete_snapshot_without_changing_rng(monkeypatch, tmp_path, act):
    target = save_fixture_path(monkeypatch, tmp_path)
    state.config.ai['api_key'] = ''
    state.current_act = act
    state.initialize_map()
    target.write_bytes(b'previous snapshot')
    before = (random.getstate(), state.map_manager.encounter_pool.rng.getstate())
    MenuAction(InputRequest(options=[]))._save_game(state)
    assert target.stat().st_size > 100
    assert list(pickletools.genops(target.read_bytes()))[-1][0].name == 'STOP'
    assert before == (random.getstate(), state.map_manager.encounter_pool.rng.getstate())
    assert not list(tmp_path.glob('.savegame-*.tmp'))
    # Full GameState deserialization is separately tracked as RUN-042.


@pytest.mark.parametrize('failure', ['dump', 'replace'])
def test_failed_save_preserves_old_snapshot_and_cleans_temporary_file(monkeypatch, tmp_path, failure):
    target = save_fixture_path(monkeypatch, tmp_path)
    target.write_bytes(b'previous snapshot')
    def fail_dump(obj, stream):
        stream.write(b'partial data')
        raise pickle.PicklingError('controlled save failure')
    def fail_replace(src, dst):
        raise OSError('controlled replace failure')
    if failure == 'dump':
        monkeypatch.setattr(pickle, 'dump', fail_dump)
    else:
        monkeypatch.setattr(os, 'replace', fail_replace)
    with pytest.raises((pickle.PicklingError, OSError), match='controlled'):
        MenuAction(InputRequest(options=[]))._save_game({'local': 'fixture'})
    assert target.read_bytes() == b'previous snapshot'
    assert not list(tmp_path.glob('.savegame-*.tmp'))
