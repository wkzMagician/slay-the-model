"""Boundary and native-entry regressions for normal-mode relic eligibility."""
from itertools import combinations
from typing import cast

import pytest

from actions.reward import AddEliteRelicAction, AddRelicAction, LoseRelicAction
from engine.card_pools import definitions as card_definitions
from engine.game_state import game_state
from engine.messages import EliteVictoryMessage
from engine.random_streams import get_rng, StreamRandom
from relics.pools import make_relic
from relics.spawn_rules import FLOOR_LIMITS, CAMPFIRE_RELICS
from utils.random import get_random_relic
from utils.types import PilePosType, RarityType


@pytest.mark.parametrize('key,limit', list(FLOOR_LIMITS.items()))
@pytest.mark.parametrize('delta', [-1,0,1])
@pytest.mark.parametrize('ascension', [0,20])
def test_floor_cutoff_boundaries(key, limit, delta, ascension):
    game_state.ascension = ascension
    game_state.current_floor = limit + delta
    game_state.player.relics = []
    relic = make_relic(key)
    assert game_state.current_floor == limit + delta
    assert relic.can_spawn() == (delta <= 0)


@pytest.mark.parametrize('key', ['TheCourier','MawBank','OldCoin','SmilingMask'])
@pytest.mark.parametrize('shop', [False,True])
def test_shop_room_exclusion_composes_with_floor_cutoff(key, shop):
    from rooms.shop import ShopRoom
    from rooms.treasure import TreasureRoom
    game_state.current_floor = 5
    game_state.current_room = ShopRoom() if shop else TreasureRoom()
    assert make_relic(key).can_spawn() == (not shop)
    game_state.current_floor = 49
    assert not make_relic(key).can_spawn()


HELD_SETS = [items for size in range(4) for items in combinations(sorted(CAMPFIRE_RELICS), size)]


@pytest.mark.parametrize('key', sorted(CAMPFIRE_RELICS))
@pytest.mark.parametrize('held', HELD_SETS)
@pytest.mark.parametrize('floor', [5,47,48])
def test_campfire_count_and_floor_are_both_required(key, held, floor):
    game_state.current_floor = floor
    game_state.player.relics = [make_relic(value) for value in held]
    assert make_relic(key).can_spawn() == (len(held) < 2 and floor < 48)


def test_campfire_eligibility_tracks_real_obtain_and_loss():
    game_state.current_floor = 5
    player = game_state.player
    player.relics = []
    pipe, shovel = make_relic('PeacePipe'), make_relic('Shovel')
    AddRelicAction(pipe).execute()
    assert make_relic('Girya').can_spawn()
    AddRelicAction(shovel).execute()
    assert not make_relic('Girya').can_spawn()
    LoseRelicAction(relic=pipe).execute()
    assert make_relic('Girya').can_spawn()


@pytest.mark.parametrize('key,target', [('BottledFlame','Anger'),('BottledLightning','Shrug It Off'),('BottledTornado','Corruption')])
def test_bottle_checks_permanent_deck_and_reacts_to_changes(key, target):
    manager = game_state.player.card_manager
    manager.piles['deck'] = []
    relic = make_relic(key)
    assert not relic.can_spawn()
    card = card_definitions()[target].make_card()
    manager.add_to_pile(card, 'hand', PilePosType.TOP)
    assert not relic.can_spawn()
    manager.add_to_pile(card.copy(), 'deck', PilePosType.TOP)
    assert relic.can_spawn()
    manager.piles['deck'].clear()
    assert not relic.can_spawn()


@pytest.mark.parametrize('key,target', [('BottledFlame','Bash'),('BottledLightning','Defend_R')])
def test_upgraded_basic_cards_remain_ineligible_for_bottles(key, target):
    card = card_definitions()[target].make_card()
    card.upgrade()
    game_state.player.card_manager.piles['deck'] = [card]
    assert not make_relic(key).can_spawn()


def test_bottles_use_original_card_metadata_for_existing_type_discrepancies():
    game_state.player.card_manager.piles['deck'] = [card_definitions()['Flame Barrier'].make_card()]
    assert make_relic('BottledLightning').can_spawn()
    assert not make_relic('BottledTornado').can_spawn()


@pytest.mark.parametrize('act', [0,1,2,3,4])
def test_ectoplasm_uses_act_number(act):
    game_state.current_act = act
    assert make_relic('Ectoplasm').can_spawn() == (act <= 1)


def test_qualification_rejection_consumes_candidate_then_uses_tail():
    game_state.current_floor = 36
    pools = game_state.relic_pools
    pools.remaining['COMMON'] = ['TinyChest','Anchor','Vajra']
    relic = get_random_relic(rarities=[RarityType.COMMON])
    assert relic is not None and relic.idstr == 'Vajra'
    assert pools.remaining['COMMON'] == ['Anchor']


@pytest.mark.parametrize('extra', [False,True])
def test_black_star_retries_same_tier_from_head_without_extra_roll(extra, monkeypatch):
    game_state.current_floor = 5
    game_state.player.relics = []
    pools = game_state.relic_pools
    pools.remaining['RARE'] = ['Girya','Ginger','Shovel','PeacePipe','Calipers']
    calls = []
    def roll(*args):
        calls.append(args)
        return 99
    monkeypatch.setattr(get_rng('relic'), 'randint', roll)
    AddEliteRelicAction(non_campfire=extra).execute()
    assert [getattr(relic,'idstr',None) for relic in game_state.player.relics] == ['Ginger' if extra else 'Girya']
    assert pools.remaining['RARE'] == (['Shovel','PeacePipe','Calipers'] if extra else ['Ginger','Shovel','PeacePipe','Calipers'])
    assert calls == [(0,99)]


def test_black_star_and_qualification_rejection_have_different_retry_scopes(monkeypatch):
    game_state.current_floor = 5
    game_state.player.relics = [make_relic('PeacePipe'),make_relic('Shovel')]
    game_state.relic_pools.remaining['RARE'] = ['Girya','Ginger','Calipers']
    monkeypatch.setattr(get_rng('relic'), 'randint', lambda *args:99)
    AddEliteRelicAction(non_campfire=True).execute()
    assert game_state.relic_pools.remaining['RARE'] == ['Ginger']
    assert getattr(game_state.player.relics[-1],'idstr',None) == 'Calipers'


def test_black_star_all_campfire_pool_reaches_ordinary_circlet(monkeypatch):
    game_state.current_floor = 5
    game_state.player.relics = []
    game_state.relic_pools.remaining['RARE'] = ['Girya','PeacePipe','Shovel']
    monkeypatch.setattr(get_rng('relic'), 'randint', lambda *args:99)
    AddEliteRelicAction(non_campfire=True).execute()
    assert getattr(game_state.player.relics[0],'idstr',None) == 'Circlet'
    assert game_state.relic_pools.remaining['RARE'] == []


def test_elite_victory_message_only_marks_black_star_extra_reward():
    from relics.global_relics.boss import BlackStar
    from rooms.combat import CombatRoom
    from utils.types import RoomType
    player = game_state.player
    player.relics = [BlackStar()]
    room = CombatRoom(room_type=RoomType.ELITE)
    room.init()
    actions = room._handle_victory()
    extras = [action for action in game_state.action_queue.queue if isinstance(action, AddEliteRelicAction)]
    bases = [action for action in actions if isinstance(action, AddEliteRelicAction)]
    assert len(extras) == len(bases) == 1
    assert cast(AddEliteRelicAction, extras[0]).non_campfire
    assert not cast(AddEliteRelicAction, bases[0]).non_campfire


def test_shop_initial_inventory_and_restock_use_shop_context(monkeypatch):
    from rooms.shop import ShopRoom
    from rooms.shop_state import ShopItem, restock_shop_item
    game_state.current_floor = 5
    game_state.relic_pools.remaining.update(COMMON=['Anchor','SmilingMask'], UNCOMMON=['HornCleat'], RARE=['Calipers'], SHOP=['TheAbacus'])
    room = ShopRoom()
    observed = []
    def generate():
        observed.append(game_state.current_room)
        relic = get_random_relic(rarities=[RarityType.COMMON], from_end=True)
        assert relic is not None and relic.idstr == 'Anchor'
        return [ShopItem('relic', relic, 150)]
    monkeypatch.setattr(room, '_generate_items', generate)
    room.init()
    assert observed == [room] and game_state.current_room is room
    game_state.relic_pools.remaining['COMMON'] = ['Vajra','MawBank']
    from types import SimpleNamespace
    rng = SimpleNamespace(random=lambda:0.0, randint=lambda low,high:low, random_float=lambda low,high:low)
    restock_shop_item(room.items[0], game_state.player, rng=rng)
    assert room.items[0].item.idstr == 'Vajra'
    room.leave()
    assert game_state.current_room is None
    assert make_relic('SmilingMask').can_spawn()
