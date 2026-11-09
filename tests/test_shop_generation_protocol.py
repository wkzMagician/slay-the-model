"""Shop phase and merchant rejection regressions with explicit prepared inputs."""
from types import SimpleNamespace
from typing import cast

import pytest

from engine.card_pools import original_id
from engine.game_state import game_state
from engine.random_streams import get_rng, StreamRandom
from rooms import shop_state
from utils.types import CardType, RarityType


def card(key, namespace='ironclad', original=None):
    return SimpleNamespace(idstr=key, namespace=namespace, rarity=RarityType.UNCOMMON,
                           _original_card_id=original or key)


@pytest.mark.parametrize('repetitions', [1,2,5])
@pytest.mark.parametrize('kind', [CardType.ATTACK,CardType.SKILL])
def test_duplicate_retries_rarity_and_full_pool(kind, repetitions, monkeypatch):
    attempts = []
    counts = {CardType.ATTACK:0,CardType.SKILL:0,CardType.POWER:0}
    rolls = []
    def rarity(rng):
        result = [RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE][len(rolls)%3]
        rolls.append(result)
        return result
    monkeypatch.setattr(shop_state,'roll_card_rarity',rarity)
    def provider(**kwargs):
        assert 'exclude_card_ids' not in kwargs
        target = kwargs['card_types'][0]
        counts[target] += 1
        attempt = counts[target]
        duplicate = target == kind and attempt <= repetitions+1
        # Different project IDs with one original ID must still be rejected.
        value = card(f'{target.name}-{attempt}', original=f'{target.name}-first' if duplicate else f'{target.name}-{attempt}')
        attempts.append((target,kwargs['rarities'][0],original_id(value)))
        return value
    cards = shop_state.generate_colored_cards(game_state.player,card_provider=provider)
    assert len(cards) == 5
    assert len(rolls) == 5+repetitions
    assert [value[1] for value in attempts] == rolls
    assert counts[kind] == repetitions+2
    assert original_id(cards[0]) != original_id(cards[1])
    assert original_id(cards[2]) != original_id(cards[3])


@pytest.mark.parametrize('slot',range(5))
def test_colorless_candidates_are_rejected_and_rarity_is_retried(slot,monkeypatch):
    calls = []
    rolls = []
    monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng: rolls.append(1) or RarityType.UNCOMMON)
    def provider(**kwargs):
        index = len(calls)
        calls.append(kwargs)
        return card(str(index),'colorless' if index == slot else 'ironclad')
    result = shop_state.generate_colored_cards(game_state.player,card_provider=provider)
    assert len(result) == 5
    assert len(calls) == len(rolls) == 6
    assert all(value.namespace != 'colorless' for value in result)


def test_empty_provider_result_finishes_without_retrying_forever(monkeypatch):
    monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng:RarityType.COMMON)
    assert shop_state.generate_colored_cards(game_state.player,card_provider=lambda **kwargs:None) == []


def test_inventory_phase_order_includes_all_prices_before_sale(monkeypatch):
    events = []
    counts = {'card':0,'relic':0,'potion':0}
    def cards(**kwargs):
        counts['card'] += 1
        events.append('candidate'+str(counts['card']))
        return card(str(counts['card']), 'colorless' if kwargs['namespaces']==['colorless'] else 'ironclad')
    def relics(**kwargs):
        counts['relic'] += 1
        events.append('relic'+str(counts['relic']))
        return object()
    def potions(**kwargs):
        counts['potion'] += 1
        events.append('potion'+str(counts['potion']))
        return object()
    class PriceRng:
        def randint(self,low,high):
            events.append('sale' if (low,high)==(0,4) else 'price')
            return low
        def random_float(self,start,end):
            events.append("price")
            return start
        def random(self):
            events.append('relic-tier')
            return 0.1
    monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng:RarityType.UNCOMMON)
    monkeypatch.setattr(shop_state,'roll_potion_rarity',lambda rng:RarityType.COMMON)
    items = shop_state.generate_shop_items(game_state.player,rng=PriceRng(),card_provider=cards,relic_provider=relics,potion_provider=potions)
    assert events == ([f'candidate{i}' for i in range(1,8)]+['price']*7+['sale']+
                      ['relic-tier','relic1','price','relic-tier','relic2','price','relic3','price']+
                      ['potion1','price','potion2','price','potion3','price'])
    assert [item.item_type for item in items] == ['card']*7+['relic']*3+['potion']*3
    assert [item.discount for item in items] == [0.5]+[0]*12


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('seed',[0,1,42,20261108])
def test_native_shop_initialization_stream_routes_and_phase_order(role,ascension,seed,monkeypatch):
    from rooms.shop import ShopRoom
    game_state.player.namespace = role
    game_state.ascension = ascension
    game_state.current_floor = 5
    game_state.player.relics = []
    events = []
    states = {}
    for name in ('card','merchant','potion','relic','card_random'):
        rng = cast(StreamRandom,get_rng(name))
        rng.seed(seed)
        states[name] = rng.export_state()
        integer, floating = rng.random_int, rng.random_float
        def draw(*args, name=name, integer=integer):
            events.append((name,'int',args))
            return integer(*args)
        def floating_draw(*args, name=name, floating=floating):
            events.append((name,'float',args))
            return floating(*args)
        monkeypatch.setattr(rng,'random_int',draw)
        monkeypatch.setattr(rng,'random_float',floating_draw)
    room = ShopRoom()
    room.init()
    groups = [value[0] for value in events]
    assert max(i for i,value in enumerate(groups) if value=='card') < groups.index('merchant')
    assert groups.index('merchant') < groups.index('potion')
    assert [item.item_type for item in room.items][-6:] == ['relic']*3+['potion']*3
    colored = [item.item for item in room.items if item.item_type=='card' and item.item.namespace!='colorless']
    assert original_id(colored[0]) != original_id(colored[1])
    assert original_id(colored[2]) != original_id(colored[3])
    assert game_state.current_room is room
    assert cast(StreamRandom,get_rng('card_random')).export_state() == states['card_random']
    assert cast(StreamRandom,get_rng('relic')).export_state() == states['relic']
    assert sum(item.discount==0.5 for item in room.items)==1
