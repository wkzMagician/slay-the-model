"""R-07: Boss treasure routing, run-wide draws, and starter upgrades."""
from typing import cast

import pytest

from actions.display import InputRequestAction
from actions.map_selection import MoveToMapNodeAction
from actions.misc import OpenChestAction
from actions.reward import AddRelicAction, AddRelicByNameAction, ChooseBossRelicAction
from engine.messages import RelicObtainedMessage
from events.neo_event import NeoEvent
from localization import set_language
from map.map_manager import MapManager
from player.player_factory import create_player
from relics.boss_pool import BossRelicPool, draw_boss_relic, draw_boss_relic_choices
from relics.character.defect import CrackedCore, FrozenCore
from relics.character.ironclad import BlackBlood, BurningBlood, MarkOfPain
from relics.character.silent import RingOfTheSerpent, RingOfTheSnake
from relics.character.watcher import HolyWater, PureWater
from relics.global_relics.common import Anchor
from relics.global_relics.special import RedCirclet
from rooms.combat import CombatRoom
from rooms.treasure import TreasureRoom
from rooms.victory import VictoryRoom
from tests.test_combat_utils import create_test_helper
from utils.random import get_random_relic
from utils.registry import get_registered
from utils.types import RarityType, RoomType


@pytest.fixture
def state():
    helper = create_test_helper()
    return helper.game_state


def request_from_queue(state) -> InputRequestAction:
    requests = [cast(InputRequestAction, action) for action in state.action_queue.queue if isinstance(action, InputRequestAction)]
    assert len(requests) == 1
    state.action_queue.clear()
    return requests[0]


@pytest.mark.parametrize('act', [1, 2])
def test_target_floor_creates_boss_chest_after_boss_node(state, act):
    manager = MapManager(seed=1, act_id=act)
    state.map_manager = manager
    state.map_data = manager.generate_map()
    manager.map_data.set_current_position(16, 0)
    state.current_act = act
    state.floor_in_act = 16
    start = manager._get_act_start_floor(act)
    MoveToMapNodeAction(start + 17, 0).execute()
    room = state.current_room
    assert isinstance(room, TreasureRoom)
    room.init()
    assert room.is_boss
    assert room.chest_type == 'boss'
    assert manager.map_data.current_floor == 17
    state.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome']
    OpenChestAction(room).execute()
    # Run the selection composer without resolving an input request.
    chooser = state.action_queue.queue[-1]
    state.action_queue.clear()
    chooser.execute()
    request = request_from_queue(state)
    assert len(request.options) == 4
    assert not state.obtained_relics


def test_regular_and_unknown_treasure_do_not_become_boss_chests(state, monkeypatch):
    manager = MapManager(seed=42)
    manager.generate_map()
    for floor in (9, 12):
        if floor == 12:
            monkeypatch.setattr(manager, '_resolve_unknown_type', lambda floor: RoomType.TREASURE)
            room = manager._create_room_instance(RoomType.UNKNOWN, floor_in_act=floor)
        else:
            room = manager.move_to_node(floor, 0)
        assert isinstance(room, TreasureRoom)
        treasure = cast(TreasureRoom, room)
        treasure.init()
        assert not treasure.is_boss
        assert treasure.chest_type in ('small', 'medium', 'large')


@pytest.mark.parametrize('act,ascension,boss_floors,victory_floor', [
    (3, 0, [16], 17), (3, 20, [16, 17], 18), (4, 0, [3], 4),
])
def test_final_acts_have_no_boss_treasure_and_a20_selects_two_bosses(state, monkeypatch, act, ascension, boss_floors, victory_floor):
    state.ascension = ascension
    manager = MapManager(seed=42, act_id=act)
    data = manager.generate_map()
    assert all(node.room_type != RoomType.TREASURE for row in data.nodes[16:] for node in row)
    indexes = []
    def encounter(**kwargs):
        indexes.append(kwargs['boss_index'])
        return [], 'test boss'
    monkeypatch.setattr(manager.encounter_pool, 'get_boss_encounter', encounter)
    start = manager._get_act_start_floor(act)
    for floor in boss_floors:
        assert isinstance(manager.move_to_node(start + floor, 0), CombatRoom)
    assert indexes == list(range(len(boss_floors)))
    assert isinstance(manager.move_to_node(start + victory_floor, 0), VictoryRoom)


@pytest.mark.parametrize('character,expected,forbidden', [
    ('Ironclad', 'MarkOfPain', 'HoveringKite'),
    ('Silent', 'HoveringKite', 'MarkOfPain'),
    ('Defect', 'Inserter', 'MarkOfPain'),
    ('Watcher', 'VioletLotus', 'MarkOfPain'),
])
def test_boss_pool_contains_shared_and_current_character_only(state, character, expected, forbidden):
    state.player = create_player(character)
    pool = BossRelicPool(42)
    pool._initialize()
    assert pool.remaining is not None
    assert 'BlackStar' in pool.remaining
    assert expected in pool.remaining
    assert forbidden not in pool.remaining
    assert len(pool.remaining) == len(set(pool.remaining))


def test_character_classes_have_one_canonical_registration():
    from relics.global_relics.boss import BlackBlood as LegacyBlackBlood, MarkOfPain as LegacyMarkOfPain
    assert LegacyBlackBlood is BlackBlood is get_registered('relic', 'BlackBlood')
    assert LegacyMarkOfPain is MarkOfPain is get_registered('relic', 'MarkOfPain')
    assert BlackBlood().namespace == MarkOfPain().namespace == 'ironclad'


def test_draws_consume_unpicked_candidates_across_acts(state):
    state.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome', 'CursedKey']
    choices = draw_boss_relic_choices()
    assert [relic.idstr for relic in choices] == ['BlackStar', 'Sozu', 'RunicDome']
    assert state.obtained_relics == set()
    state.current_act = 2
    state.initialize_map()
    assert draw_boss_relic().idstr == 'CursedKey'
    assert isinstance(draw_boss_relic(), RedCirclet)


def test_pool_uses_reproducible_rng_independent_of_other_draws(state):
    import random
    state.player = create_player('Ironclad')
    first = BossRelicPool(42)
    second = BossRelicPool(42)
    first._initialize()
    random.seed(123)
    for _ in range(50):
        random.random()
    second._initialize()
    assert first.remaining == second.remaining


@pytest.mark.parametrize('remaining,expected', [
    ([], ['RedCirclet'] * 3),
    (['BlackStar'], ['BlackStar', 'RedCirclet', 'RedCirclet']),
    (['BlackBlood'], ['RedCirclet'] * 3),
])
def test_empty_short_and_ineligible_pools_use_repeatable_red_circlet(state, remaining, expected):
    state.player.relics = []
    state.boss_relic_pool.remaining = list(remaining)
    assert [relic.idstr for relic in draw_boss_relic_choices()] == expected
    AddRelicAction(RedCirclet()).execute()
    AddRelicAction(RedCirclet()).execute()
    assert len(state.player.relics) == 2
    assert isinstance(draw_boss_relic(), RedCirclet)
    assert RedCirclet().rarity == RarityType.SPECIAL


@pytest.mark.parametrize('starter,upgrade', [
    (BurningBlood, BlackBlood), (RingOfTheSnake, RingOfTheSerpent),
    (CrackedCore, FrozenCore), (PureWater, HolyWater),
])
def test_spawn_requires_starter_and_acquisition_replaces_its_slot_once(state, monkeypatch, starter, upgrade):
    relic = upgrade()
    assert not relic.can_spawn()
    initial = starter()
    # Match by ID even if the starter is not in slot zero.
    state.player.relics = [Anchor(), initial]
    assert relic.can_spawn()
    events = []
    original_publish = state.publish_message
    def publish(message):
        if isinstance(message, RelicObtainedMessage):
            events.append(message)
        return original_publish(message)
    monkeypatch.setattr(state, 'publish_message', publish)
    AddRelicByNameAction(relic.idstr).execute()
    state.drive_actions()
    assert len(state.player.relics) == 2
    assert isinstance(state.player.relics[0], Anchor)
    assert isinstance(state.player.relics[1], upgrade)
    assert initial not in state.player.relics
    assert len(events) == 1
    assert relic.idstr in state.obtained_relics
    assert starter.__name__ in state.obtained_relics
    assert not relic.can_spawn()
    AddRelicAction(upgrade()).execute()
    assert len(events) == 1
    if upgrade is RingOfTheSerpent:
        assert state.player.base_draw_count == 6


def test_black_blood_replaces_burning_blood_effect_in_real_combat(state):
    helper = create_test_helper()
    player = helper.create_player(hp=30, max_hp=80)
    player.relics = [BurningBlood()]
    AddRelicAction(BlackBlood()).execute()
    helper.start_combat([])
    helper.game_state.drive_actions()
    assert helper.game_state.current_combat is not None
    helper.game_state.current_combat._check_combat_end()
    assert player.hp == 42


@pytest.mark.parametrize('starter,upgrade', [
    (BurningBlood, BlackBlood), (RingOfTheSnake, RingOfTheSerpent),
    (CrackedCore, FrozenCore), (PureWater, HolyWater),
])
def test_neow_loses_starter_before_shared_pool_draw(state, starter, upgrade):
    state.player.relics = [starter()]
    state.obtained_relics.add(starter.__name__)
    state.boss_relic_pool.remaining = [upgrade.__name__, 'BlackStar', 'Sozu']
    NeoEvent()._show_four_blessings()
    request = request_from_queue(state)
    for action in request.options[-1].actions:
        action.execute()
    state.drive_actions()
    assert [relic.idstr for relic in state.player.relics] == ['BlackStar']
    assert state.boss_relic_pool.remaining == ['Sozu']
    assert starter.__name__ in state.obtained_relics


def test_cached_candidates_skip_and_duplicate_open_do_not_redraw_or_obtain(state):
    state.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome', 'CursedKey']
    room = TreasureRoom(is_boss=True)
    room.init()
    first = room._get_boss_chest_contents()['relics']
    assert room.boss_relic_choices() is first
    OpenChestAction(room).execute()
    assert len(state.action_queue.queue) == 1
    chooser = state.action_queue.queue[0]
    state.action_queue.clear()
    OpenChestAction(room).execute()
    assert state.action_queue.is_empty()
    chooser.execute()
    chooser.execute()
    request = request_from_queue(state)
    assert len(request.options) == 4
    for action in request.options[-1].actions:
        action.execute()
    state.drive_actions()
    assert room.should_leave
    assert room.boss_choice_resolved
    assert state.player.relics == []
    assert state.obtained_relics == set()
    assert state.boss_relic_pool.remaining == ['CursedKey']
    # A stale selection after skip cannot obtain a relic.
    request.options[0].actions[0].execute()
    ChooseBossRelicAction(room=room).execute()
    assert state.player.relics == []
    assert state.action_queue.is_empty()


def test_selection_obtains_one_relic_and_exits_room(state):
    state.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome']
    room = TreasureRoom(is_boss=True)
    room.init()
    chooser = ChooseBossRelicAction(room=room)
    chooser.execute()
    request = request_from_queue(state)
    request.options[0].actions[0].execute()
    request.options[0].actions[0].execute()
    state.drive_actions()
    assert [relic.idstr for relic in state.player.relics] == ['BlackStar']
    assert room.should_leave
    assert room.boss_choice_resolved


def test_random_boss_rewards_use_shared_pool_and_exclusions(state):
    state.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome']
    relic = get_random_relic(rarities=[RarityType.BOSS], exclude=['BlackStar'])
    assert relic is not None
    assert relic.idstr == 'Sozu'
    assert state.boss_relic_pool.remaining == ['RunicDome']


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_red_circlet_is_localized(language):
    set_language(language)
    relic = RedCirclet()
    assert 'relics.' not in relic.info()
    assert relic.local('name').resolve() != 'RedCirclet'


def test_open_chest_runs_through_runtime_input_and_leaves_after_one_choice(state):
    state.config.mode = "debug"
    state.config.debug["select_type"] = "first"
    state.boss_relic_pool.remaining = ["BlackStar", "Sozu", "RunicDome"]
    room = TreasureRoom(is_boss=True)
    room.init()
    state.action_queue.add_action(OpenChestAction(room))
    state.drive_actions()
    assert [relic.idstr for relic in state.player.relics] == ["BlackStar"]
    assert room.should_leave
    assert state.pending_input_request is None


def test_mark_of_pain_remains_functional_after_moving_to_character_module():
    from enemies.act1.cultist import Cultist
    from cards.colorless.wound import Wound

    helper = create_test_helper()
    player = helper.game_state.player
    player.relics = [MarkOfPain()]
    enemy = helper.create_enemy(Cultist, hp=100)
    combat = helper.start_combat([enemy])
    helper.game_state.drive_actions()
    wounds = [card for card in player.card_manager.get_pile("draw_pile") if isinstance(card, Wound)]
    assert len(wounds) == 2
    combat._start_player_turn()
    helper.game_state.drive_actions()
    assert player.energy == player.max_energy + 1
