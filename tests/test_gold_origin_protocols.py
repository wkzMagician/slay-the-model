"""Gold creation, receipt, real event options, map moves and lethal plays."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

import actions.reward as reward_actions
from actions.display import InputRequestAction
from actions.map_selection import MoveToMapNodeAction
from actions.misc import OpenChestAction
from actions.reward import AddGoldAction
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from engine.messages import GoldGainedMessage
from engine.random_streams import get_rng
from events.dead_adventurer import DeadAdventurer
from events.the_ssssserpent import TheSsssserpent
from events.tomb_of_lord_red_mask import TombOfLordRedMask
from events.world_of_goop import WorldOfGoop
from map.map_manager import MapManager
from map.map_node import MapNode
from player.player_factory import create_player
from relics.global_relics.boss import Ectoplasm
from relics.global_relics.event import BloodyIdol, GoldenIdol, RedMask, SsserpentHead
from rooms.combat import CombatRoom
from rooms.treasure import TreasureRoom
from tests.test_deferred_damage_protocols import play, prepare
from utils.result_types import GameTerminalState
from utils.types import RoomType

REFERENCE = json.loads(gzip.decompress((Path(__file__).parent / 'fixtures/gold_origin_reference.json.gz').read_bytes()))
ROLES = ['ironclad', 'silent', 'defect', 'watcher']


def player_with_relics(role='ironclad', idol=True, bloody=True, ectoplasm=False):
    player = create_player(role)
    game_state.player = player
    player.relics = ([GoldenIdol()] if idol else []) + ([BloodyIdol()] if bloody else []) + ([Ectoplasm()] if ectoplasm else [])
    player.gold = 100
    player.hp = player.max_hp - 20
    return player


@pytest.mark.parametrize('row', REFERENCE['receipts'])
def test_original_reward_creation_and_actual_gain_gold(row, monkeypatch):
    player = player_with_relics(idol=row['idol'], ectoplasm=row['ectoplasm'])
    hp = player.hp
    seen = []
    original = reward_actions.publish_message

    def publish(message):
        if isinstance(message, GoldGainedMessage):
            seen.append((message.amount, player.gold))
        return original(message)

    monkeypatch.setattr(reward_actions, 'publish_message', publish)
    rng_before = game_state.random_streams.export_state()
    action = AddGoldAction(row['base'], source=row['source'])
    assert action.amount == row['amount']
    action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == row['gold']
    assert [gold for _, gold in seen] == row['callbacks']
    assert [amount for amount, _ in seen] == [row['amount']] * len(row['callbacks'])
    assert player.hp == hp + 5 * len(row['callbacks'])
    assert game_state.random_streams.export_state() == rng_before


@pytest.mark.parametrize('base,ascension,expected', REFERENCE['boss_arithmetic'])
def test_original_boss_arithmetic_and_one_misc_draw(base, ascension, expected, monkeypatch):
    game_state.ascension = ascension
    calls = []

    def draw(start, end):
        calls.append((start, end))
        return base

    monkeypatch.setattr(get_rng('misc'), 'randint', draw)
    assert CombatRoom(room_type=RoomType.BOSS)._calculate_gold_reward() == expected
    assert calls == [(95, 105)]


@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('ascension', [0, 12, 13, 20])
@pytest.mark.parametrize('act', [1, 2])
@pytest.mark.parametrize('base', [95, 100, 105])
@pytest.mark.parametrize('idol', [False, True])
def test_lethal_boss_play_creates_modified_reward(role, ascension, act, base, idol, monkeypatch):
    player, enemies, combat = prepare(role, ascension, health=(6,))
    player.relics = [GoldenIdol(), BloodyIdol()] if idol else []
    game_state.current_act = act
    room = CombatRoom(enemies=enemies, room_type=RoomType.BOSS)
    room.combat = combat
    game_state.current_room = room
    hp, gold = player.hp, player.gold
    assert play(Strike()) is None
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN
    monkeypatch.setattr(get_rng('misc'), 'randint', lambda *_: base)
    actions = room._handle_victory()
    action = next(action for action in actions if isinstance(action, AddGoldAction))
    reduced = next(row[2] for row in REFERENCE['boss_arithmetic'] if row[:2] == [base, ascension])
    expected = next(row for row in REFERENCE['receipts'] if row['base'] == reduced and row['source'] == 'combat'
                    and row['idol'] == idol and not row['ectoplasm'])
    assert action.amount == expected['amount']
    action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == gold + expected['amount']
    assert player.hp == min(player.max_hp, hp + (5 if idol else 0))


@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('act', [1, 2, 3])
@pytest.mark.parametrize('roll', [1, 11, 13, 100])
@pytest.mark.parametrize('idol,bloody,ectoplasm', [(False, False, False), (True, False, False), (False, True, False),
                                                 (True, True, False), (False, False, True), (True, False, True),
                                                 (False, True, True), (True, True, True)])
def test_unknown_map_move_snake_uses_gold_receipt(role, act, roll, idol, bloody, ectoplasm, monkeypatch):
    player = player_with_relics(role, idol, bloody, ectoplasm)
    player.relics.append(SsserpentHead())
    hp = player.hp
    game_state.current_act = act
    manager = MapManager(seed=1, act_id=act, random_streams=game_state.random_streams)
    start = manager._get_act_start_floor(act)
    manager.map_data.nodes = [[MapNode(start, 0, RoomType.NEO, connections_up=[0])],
                              [MapNode(start + 1, 0, RoomType.UNKNOWN)]]
    manager.map_data.set_current_position(0, 0)
    game_state.map_manager = manager
    game_state.current_act = act
    game_state.current_floor = start
    monkeypatch.setattr(get_rng('event'), 'randint', lambda *_: roll)
    MoveToMapNodeAction(start + 1, 0).execute()
    assert game_state.drive_actions() is None
    assert player.gold == 100 + (0 if ectoplasm else 50)
    assert player.hp == hp + (5 if bloody and not ectoplasm else 0)


@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('ascension', [0, 12, 13, 20])
@pytest.mark.parametrize('event_type,amount', [(TombOfLordRedMask, 222), (WorldOfGoop, 75), (TheSsssserpent, None)])
@pytest.mark.parametrize('ectoplasm', [False, True])
def test_real_event_options_preserve_fixed_gold(role, ascension, event_type, amount, ectoplasm):
    player = player_with_relics(role, ectoplasm=ectoplasm)
    game_state.ascension = ascension
    if event_type is TombOfLordRedMask:
        player.relics.append(RedMask())
    event_type().trigger()
    menu = cast(InputRequestAction, game_state.action_queue.queue[-1])
    game_state.action_queue.clear()
    option = menu.options[0]
    if amount is None:
        amount = 150 if ascension >= 15 else 175
    for action in option.actions:
        game_state.add_action(action)
    assert game_state.drive_actions() is None
    assert player.gold == 100 + (0 if ectoplasm else amount)


@pytest.mark.parametrize('size', ['small', 'medium', 'large'])
def test_actual_chest_excludes_golden_idol(size, monkeypatch):
    player = player_with_relics()
    room = TreasureRoom()
    room.chest_type = size
    game_state.current_room = room
    monkeypatch.setattr(get_rng('treasure'), 'random', lambda: .1)
    OpenChestAction(room).execute()
    action = next(action for action in game_state.action_queue.queue if isinstance(action, AddGoldAction))
    game_state.action_queue.clear()
    amount = cast(AddGoldAction, action).amount
    assert amount in {'small': range(23,29), 'medium': range(45,56), 'large': range(68,84)}[size]
    action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == 100 + amount


@pytest.mark.parametrize('initial,final,expected', [(True, False, 23), (False, True, 18)])
def test_reward_bonus_is_fixed_at_creation(initial, final, expected):
    player = player_with_relics(idol=initial, bloody=False)
    action = AddGoldAction(18, source='combat')
    player.relics = [GoldenIdol()] if final else []
    action.execute()
    assert player.gold == 100 + expected


def test_legacy_action_without_source_is_direct():
    player = player_with_relics()
    action = AddGoldAction.__new__(AddGoldAction)
    action.amount, action.chance = 50, 1.0
    action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == 150


@pytest.mark.parametrize('act', [3, 4])
def test_later_bosses_keep_existing_no_reward_exit(act):
    prepare()
    game_state.current_act = act
    room = CombatRoom(room_type=RoomType.BOSS)
    assert not any(isinstance(action, AddGoldAction) for action in room._handle_victory())

@pytest.mark.parametrize('room_type,base', [(RoomType.MONSTER, 18), (RoomType.ELITE, 33)])
@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('ectoplasm', [False, True])
def test_normal_and_elite_victory_reward_sources(room_type, base, role, ectoplasm, monkeypatch):
    player, enemies, combat = prepare(role, health=(6,))
    player.relics = [GoldenIdol(), BloodyIdol()] + ([Ectoplasm()] if ectoplasm else [])
    room = CombatRoom(enemies=enemies, room_type=room_type)
    room.combat = combat
    hp, gold = player.hp, player.gold
    assert play(Strike()) is None
    monkeypatch.setattr(get_rng('treasure'), 'randint', lambda *_: base)
    action = next(action for action in room._handle_victory() if isinstance(action, AddGoldAction))
    expected = next(row for row in REFERENCE['receipts'] if row['source'] == 'combat' and row['base'] == base
                    and row['idol'] and row['ectoplasm'] == ectoplasm)
    assert action.amount == expected['amount']
    action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == gold + expected['gold'] - 100
    assert player.hp == min(player.max_hp, hp + (0 if ectoplasm else 5))


@pytest.mark.parametrize('event_name', ['dead_adventurer', 'mysterious_sphere', 'the_colosseum', 'mind_bloom'])
@pytest.mark.parametrize('idol', [False, True])
@pytest.mark.parametrize('ectoplasm', [False, True])
def test_existing_event_combat_gold_producers(event_name, idol, ectoplasm, monkeypatch):
    from actions.combat import StartFightAction
    from events.mind_bloom import MindBloom
    from events.mysterious_sphere import MysteriousSphere
    from events.the_colosseum import TheColosseum

    player = player_with_relics(idol=idol, ectoplasm=ectoplasm)
    if event_name == 'dead_adventurer':
        event = DeadAdventurer()
        event.search_count = 1
        # Prepare the event's combat roll and bonus amount independently.
        monkeypatch.setattr(get_rng('misc'), 'randint', lambda lo, hi: 1 if hi == 100 else 33)
        event.trigger()
    elif event_name == 'mysterious_sphere':
        monkeypatch.setattr(get_rng('misc'), 'randint', lambda *_: 50)
        MysteriousSphere().trigger()
    elif event_name == 'the_colosseum':
        event = TheColosseum()
        event.first_fight_done = True
        event.trigger()
    else:
        MindBloom()._start_war(25)
    if event_name == 'mind_bloom':
        fight = next(action for action in game_state.action_queue.queue if isinstance(action, StartFightAction))
    else:
        menu = cast(InputRequestAction, game_state.action_queue.queue[-1])
        fight = next(action for action in menu.options[0].actions if isinstance(action, StartFightAction))
    rewards = [action for action in cast(StartFightAction, fight).victory_actions if isinstance(action, AddGoldAction)]
    bases = {'dead_adventurer': [30, 33], 'mysterious_sphere': [50], 'the_colosseum': [100], 'mind_bloom': [25]}[event_name]
    expected = [base + (int(base * .25 + .5) if idol else 0) for base in bases]
    assert [action.amount for action in rewards] == expected
    game_state.action_queue.clear()
    for action in rewards:
        action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == 100 + (0 if ectoplasm else sum(expected))


def test_dead_adventurer_immediate_search_gold_is_direct(monkeypatch):
    player = player_with_relics()
    event = DeadAdventurer()
    monkeypatch.setattr(get_rng('misc'), 'choice', lambda _: 'gold')
    actions = event._get_search_reward_actions()
    for action in actions:
        action.execute()
    assert game_state.drive_actions() is None
    assert player.gold == 130


def test_failed_chance_skips_receipt_and_keeps_single_misc_draw(monkeypatch):
    player = player_with_relics()
    hp = player.hp
    calls = []

    def draw():
        calls.append('draw')
        return .9

    monkeypatch.setattr(get_rng('misc'), 'random', draw)
    AddGoldAction(50, chance=.7).execute()
    assert game_state.drive_actions() is None
    assert player.gold == 100 and player.hp == hp
    assert calls == ['draw']
