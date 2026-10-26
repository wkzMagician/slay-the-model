"""Native behavior for Gambling Chip, Incense Burner, and Wing Boots."""
import pickle
from typing import cast

import pytest

from actions.card import DrawCardsAction
from actions.card_choice import GamblingChipAction
from actions.combat import DealDamageAction, LoseHPAction
from actions.map_selection import MoveToMapNodeAction, SelectMapNodeAction
from actions.reward import AddRelicAction
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import CardDiscardedMessage, CardDrawnMessage, RoundEndedMessage
from map.map_manager import MapManager
from map.map_node import MapNode
from player.player_factory import create_player
from relics.character.silent import ToughBandages
from relics.global_relics.common import Anchor
from relics.global_relics.rare import GamblingChip, IncenseBurner, WingBoots
from tests.test_combat_utils import create_test_helper
from utils.registry import get_registered
from utils.types import DamageType, RarityType, RoomType


def setup_combat(relic):
    helper = create_test_helper()
    gs = helper.game_state
    player = create_player('Ironclad')
    gs.player = player
    player.relics = []
    player.max_hp = player.hp = 10000
    player.card_manager.piles['deck'] = [Defend() for _ in range(20)]
    gs.add_action(AddRelicAction(relic))
    gs.drive_actions()
    combat = helper.start_combat([Cultist(), Cultist()])
    gs.drive_actions()
    return helper, combat, player


@pytest.mark.parametrize('cls', [GamblingChip, IncenseBurner, WingBoots])
def test_relic_is_exported_registered_and_in_native_rare_pool(cls, monkeypatch):
    import relics
    import relics.global_relics as global_relics
    import random
    from utils.random import get_random_relic

    helper = create_test_helper()
    helper.game_state.player = create_player('Ironclad')
    helper.game_state.player.relics = []
    helper.game_state.current_floor = 1
    seen = []
    choose = random.choice

    def observe(sequence):
        seen.extend(sequence)
        return choose(sequence)

    monkeypatch.setattr(random, 'choice', observe)
    get_random_relic(characters=['ironclad'], rarities=[RarityType.RARE])
    assert cls.__name__ in seen
    assert get_registered('relic', cls.__name__) is cls
    assert getattr(relics, cls.__name__) is cls
    assert getattr(global_relics, cls.__name__) is cls


@pytest.mark.parametrize('selected', [[], [0], [0, 2], list(range(5))])
def test_chip_opens_after_five_draws_and_replaces_only_the_selection(selected, monkeypatch):
    helper, combat, player = setup_combat(GamblingChip())
    gs = helper.game_state
    observed = []

    def select(request):
        observed.append(list(player.card_manager.piles['hand']))
        assert len(request.options) == 5
        return selected

    monkeypatch.setattr(gs, '_resolve_debug_selection', select)
    combat._execute_player_start_phase()
    assert len(observed) == 1
    opening = observed[0]
    assert len(player.card_manager.piles['hand']) == 5
    assert player.card_manager.piles['discard_pile'] == [opening[i] for i in selected]
    for i, card in enumerate(opening):
        assert (card in player.card_manager.piles['hand']) == (i not in selected)
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._execute_next_phase()
    combat._execute_next_phase()
    assert len(observed) == 1
    combat = helper.start_combat([Cultist()])
    gs.drive_actions()
    combat._execute_player_start_phase()
    assert len(observed) == 2


def test_chip_discards_all_before_drawing_and_triggers_manual_discard_relics(monkeypatch):
    helper, combat, player = setup_combat(GamblingChip())
    player.relics.append(ToughBandages())
    events = []
    publish = helper.game_state.publish_message

    def observe(message, *args, **kwargs):
        if isinstance(message, (CardDiscardedMessage, CardDrawnMessage)):
            events.append(type(message).__name__)
        return publish(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, 'publish_message', observe)
    combat._execute_player_start_phase()
    assert events == ['CardDrawnMessage'] * 5 + ['CardDiscardedMessage'] * 5 + ['CardDrawnMessage'] * 5
    assert player.block == 15
    assert combat.combat_state.discarded_cards_this_turn == 5


@pytest.mark.parametrize('draw_count', [0, 2, 5])
def test_chip_empty_hand_or_empty_draw_pile_finishes_without_losing_cards(draw_count):
    helper = create_test_helper()
    player = helper.game_state.player
    player.card_manager.piles['hand'] = [Strike() for _ in range(draw_count)]
    originals = list(player.card_manager.piles['hand'])
    helper.game_state.add_action(GamblingChipAction())
    helper.game_state.drive_actions()
    assert set(player.card_manager.piles['hand']) == set(originals)
    assert not player.card_manager.piles['discard_pile']


def test_incense_counts_across_combats_and_expires_after_all_enemies():
    burner = IncenseBurner()
    helper, combat, player = setup_combat(burner)
    for _ in range(5):
        combat._execute_player_start_phase()
        assert player.get_power('Intangible') is None
    assert burner.counter == 5
    combat = helper.start_combat([Cultist(), Cultist()])
    helper.game_state.drive_actions()
    combat._execute_player_start_phase()
    assert burner.counter == 0
    intangible = player.get_power('Intangible')
    assert intangible is not None and intangible.duration == 1
    for enemy in combat.enemies:
        old_hp = player.hp
        helper.game_state.add_action(DealDamageAction(20, target=player, source=enemy, damage_type=DamageType.PHYSICAL))
        helper.game_state.drive_actions()
        assert old_hp - player.hp == 1
    helper.game_state.add_action(LoseHPAction(amount=9, target=player))
    hp = player.hp
    helper.game_state.drive_actions()
    assert hp - player.hp == 1
    combat._end_player_phase()
    combat.execute_enemy_phase()
    assert player.get_power('Intangible') is None


def test_incense_triggers_again_on_twelfth_turn_and_obtain_broadcast_does_not_reset():
    burner = IncenseBurner()
    helper, combat, player = setup_combat(burner)
    for turn in range(1, 13):
        combat._execute_player_start_phase()
        assert bool(player.get_power('Intangible')) == (turn % 6 == 0)
        helper.game_state.publish_message(RoundEndedMessage(owner=player, enemies=combat.enemies))
        helper.game_state.drive_actions()
        if turn == 5:
            helper.game_state.add_action(AddRelicAction(Anchor()))
            helper.game_state.drive_actions()
            assert burner.counter == 5
    assert burner.counter == 0


def setup_map(charges=3, act=1):
    helper = create_test_helper()
    helper.game_state.current_act = act
    player = helper.game_state.player
    boots = WingBoots()
    boots.charges = charges
    player.relics = [boots]
    manager = MapManager(seed=1, act_id=act)
    start = manager._get_act_start_floor(act)
    manager.map_data.nodes = [
        [MapNode(start + floor, position, RoomType.REST, connections_up=[0]) for position in range(2)]
        for floor in range(5)
    ]
    helper.game_state.map_manager = manager
    return helper.game_state, manager, boots, start


@pytest.mark.parametrize('act', [1, 2, 3])
def test_wings_normal_move_free_and_cross_path_consumes_one(act):
    gs, manager, boots, start = setup_map(act=act)
    assert [node.position for node in manager.get_available_moves()] == [0, 1]
    MoveToMapNodeAction(start + 1, 0).execute()
    assert boots.charges == 3
    MoveToMapNodeAction(start + 2, 1).execute()
    assert boots.charges == 2
    assert manager.map_data.current_position == 1
    assert gs.current_room is not None
    assert gs.current_room.room_type == RoomType.REST


def test_wings_third_jump_exhausts_and_normal_moves_remain_available():
    _, manager, boots, start = setup_map()
    for floor in range(1, 4):
        manager.move_to_node(start + floor, 1)
    assert boots.charges == 0
    assert [node.position for node in manager.get_available_moves()] == [0]
    with pytest.raises(ValueError):
        manager.move_to_node(start + 4, 1)
    manager.move_to_node(start + 4, 0)
    assert boots.charges == 0


@pytest.mark.parametrize('floor,position', [(0, 0), (2, 0), (-1, 0), (1, -1), (1, 99)])
def test_invalid_wing_moves_do_not_mutate_position_or_charges(floor, position):
    _, manager, boots, start = setup_map()
    with pytest.raises(ValueError):
        manager.move_to_node(start + floor, position)
    assert boots.charges == 3
    assert (manager.map_data.current_floor, manager.map_data.current_position) == (0, 0)
    assert manager.map_data.visited_path == []


def test_wings_room_creation_failure_does_not_consume_charge(monkeypatch):
    _, manager, boots, start = setup_map()

    def fail(*args, **kwargs):
        raise RuntimeError('room failed')

    monkeypatch.setattr(manager, '_create_room_instance', fail)
    with pytest.raises(RuntimeError):
        manager.move_to_node(start + 1, 1)
    assert boots.charges == 3
    assert manager.map_data.current_floor == 0


def test_map_selection_composer_offers_extra_paths_without_charging(monkeypatch):
    gs, manager, boots, _ = setup_map()
    offered = []
    action = SelectMapNodeAction()
    monkeypatch.setattr(action, '_make_decision', lambda manager, moves: offered.extend(moves))
    action.execute()
    assert len(offered) == 2
    assert boots.charges == 3


def test_existing_path_order_is_preserved_before_extra_wing_choices():
    gs, manager, boots, start = setup_map()
    current = manager.map_data.get_current_node()
    assert current is not None
    current.connections_up = [1, 0]
    manager.map_data.nodes[1].append(MapNode(start + 1, 2, RoomType.REST))
    gs.player.relics = []
    assert [node.position for node in manager.get_available_moves()] == [1, 0]
    gs.player.relics = [boots]
    assert [node.position for node in manager.get_available_moves()] == [1, 0, 2]


def test_wing_charges_and_incense_counter_survive_serialization_and_act_change():
    gs, _, boots, _ = setup_map(charges=2)
    burner = IncenseBurner()
    burner.counter = 5
    boots, burner = pickle.loads(pickle.dumps((boots, burner)))
    gs.player.relics = [boots, burner]
    next_map = MapManager(seed=2, act_id=2)
    next_map.generate_map()
    assert boots.charges == 2
    assert burner.counter == 5


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_descriptions_and_counter_display(language):
    from localization import set_language

    set_language(language)
    try:
        for relic in [GamblingChip(), IncenseBurner(), WingBoots()]:
            assert not relic.display_name().startswith('relics.')
            assert not relic.display_description().startswith('relics.')
        boots = WingBoots()
        assert '3' in boots.status_text()
        boots.charges = 0
        assert boots.status_text()
        assert '{remaining}' not in boots.display_description()
    finally:
        set_language('en')
