"""Courier threshold, retry timing and real menu-purchase regressions."""
from typing import cast

import pytest

from actions.misc import BuyItemAction
from actions.reward import AddRelicAction
from engine.card_pools import definitions, original_rarity
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.global_relics.uncommon import TheCourier
from relics.pools import make_relic
from rooms import shop_state
from rooms.shop import ShopRoom
from utils.compatible_random import float32
from utils.types import RarityType


@pytest.mark.parametrize('kind',['card','potion','relic'])
@pytest.mark.parametrize('rarity',[RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE,RarityType.SHOP])
def test_courier_hook_allows_merchandise(kind,rarity):
    relic=make_relic('MembershipCard' if rarity==RarityType.SHOP else 'Anchor')
    relic.rarity=rarity
    assert TheCourier().should_restock_shop_item(kind,relic)


@pytest.mark.parametrize('kind',['remove','card_removal'])
def test_courier_hook_excludes_removal_service(kind):
    assert not TheCourier().should_restock_shop_item(kind)


@pytest.mark.parametrize('old_tier',[RarityType.UNCOMMON,RarityType.RARE])
@pytest.mark.parametrize('value,rare',[
    (0.0,True),(float32(float32(0.3)-2**-25),True),(float32(0.3),False),
    (float32(float32(0.3)+2**-25),False),(float32(1-2**-24),False),
])
def test_colorless_threshold_is_float32_strict_and_ignores_old_tier(old_tier,value,rare):
    events=[]
    class Rng:
        def random(self):
            events.append('tier')
            return value
        def random_float(self,low,high):
            events.append('price')
            return 1.0
    def provider(**kwargs):
        events.append(kwargs)
        assert kwargs['rarities']==[RarityType.RARE if rare else RarityType.UNCOMMON]
        assert kwargs['namespaces']==['colorless']
        return definitions()['Apotheosis' if rare else 'Finesse'].make_card()
    item=shop_state.ShopItem('card',definitions()['Finesse' if old_tier==RarityType.UNCOMMON else 'Apotheosis'].make_card(),100,0.5)
    shop_state.restock_shop_item(item,game_state.player,rng=Rng(),card_provider=provider)
    assert original_rarity(item.item)==(RarityType.RARE if rare else RarityType.UNCOMMON)
    assert item.base_price==(180 if rare else 90)
    assert item.discount==0 and not item.purchased
    assert events[0]=='tier' and events[-1]=='price' and len(events)==3


def test_four_rejections_reroll_tiers_and_price_only_final_candidate():
    values=iter([0.9,0.1,0.1,0.6,0.9])
    candidates=iter([make_relic(key) for key in ['OldCoin','SmilingMask','MawBank','TheCourier','Ginger']])
    events=[]
    class Rng:
        def random(self):
            events.append('tier')
            return next(values)
        def random_float(self,low,high):
            events.append('price')
            return 1.0
    def provider(**kwargs):
        events.append(kwargs)
        assert kwargs['from_end'] and 'exclude' not in kwargs
        return next(candidates)
    item=shop_state.ShopItem('relic',make_relic('Anchor'),150)
    shop_state.restock_shop_item(item,game_state.player,rng=Rng(),relic_provider=provider)
    assert item.item.idstr=='Ginger' and item.base_price==300
    assert events[-1]=='price' and events.count('price')==1 and events.count('tier')==5
    assert [value['rarities'][0] for value in events if isinstance(value,dict)]==[
        RarityType.RARE,RarityType.COMMON,RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE]


def test_shop_qualification_rejection_consumes_tail_without_outer_reroll():
    game_state.current_floor=5
    game_state.current_room=ShopRoom()
    game_state.relic_pools.remaining['COMMON']=['Anchor','SmilingMask','MawBank']
    events=[]
    class Rng:
        def random(self):
            events.append('tier')
            return 0.1
        def random_float(self,low,high):
            events.append('price')
            return 1.0
    item=shop_state.ShopItem('relic',make_relic('MembershipCard'),150)
    shop_state.restock_shop_item(item,game_state.player,rng=Rng())
    assert item.item.idstr=='Anchor'
    assert game_state.relic_pools.remaining['COMMON']==[]
    assert events==['tier','price']


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('seed',[0,1,42])
def test_actual_shop_tier_relic_purchase_reopens_slot_and_second_purchase(role,ascension,seed,monkeypatch):
    game_state.player.namespace=role
    game_state.ascension=ascension
    game_state.current_floor=5
    game_state.player.relics=[]
    AddRelicAction(make_relic('TheCourier')).execute()
    game_state.player.gold=10000
    cast(StreamRandom,get_rng('merchant')).seed(seed)
    game_state.relic_pools.remaining['RARE']=['Ginger','Calipers','Turnip']
    room=ShopRoom()
    item=shop_state.ShopItem('relic',make_relic('MembershipCard'),150)
    room.items=[item]
    game_state.current_room=room
    monkeypatch.setattr(shop_state,'roll_relic_rarity',lambda rng:RarityType.RARE)
    for _ in range(2):
        menu=room._build_shop_menu()
        action=next(action for option in menu.options for action in option.actions if isinstance(action,BuyItemAction) and action.shop_item is item)
        previous=item.item
        gold=game_state.player.gold
        quote=item.get_final_price_with_modifiers(ascension,game_state)
        action.execute()
        assert game_state.player.gold==gold-quote
        assert item.item is not previous
        assert item.item.rarity==RarityType.RARE
        assert not item.purchased and item.discount==0 and item.quoted_price is not None
        assert previous.idstr in game_state.obtained_relics
    assert 'MembershipCard' in game_state.obtained_relics


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('seed',[0,1,42])
@pytest.mark.parametrize('old_tier',[RarityType.UNCOMMON,RarityType.RARE])
@pytest.mark.parametrize('membership',[False,True])
def test_actual_colorless_purchase_and_restock_twice(role,ascension,seed,old_tier,membership):
    game_state.player.namespace=role
    game_state.ascension=ascension
    game_state.player.relics=[]
    AddRelicAction(make_relic('TheCourier')).execute()
    if membership: AddRelicAction(make_relic('MembershipCard')).execute()
    game_state.player.gold=10000
    cast(StreamRandom,get_rng('merchant')).seed(seed)
    cast(StreamRandom,get_rng('card')).seed(seed+1)
    room=ShopRoom()
    old=definitions()['Finesse' if old_tier==RarityType.UNCOMMON else 'Apotheosis'].make_card()
    item=shop_state.ShopItem('card',old,100,0.5)
    room.items=[item]
    game_state.current_room=room
    before=len(game_state.player.card_manager.get_pile('deck'))
    for _ in range(2):
        menu=room._build_shop_menu()
        action=next(action for option in menu.options for action in option.actions if isinstance(action,BuyItemAction) and action.shop_item is item)
        old=item.item
        gold=game_state.player.gold
        price=item.get_final_price_with_modifiers(ascension,game_state)
        action.execute()
        assert game_state.player.gold==gold-price
        assert item.item is not old and item.item.namespace=='colorless'
        assert item.discount==0 and not item.purchased
    assert len(game_state.player.card_manager.get_pile('deck'))==before+2


def test_no_candidate_keeps_sold_slot_and_does_not_roll_price():
    class Rng:
        def random(self): return 0.1
        def random_float(self,*args): raise AssertionError('empty candidate must not receive a price')
    item=shop_state.ShopItem('relic',make_relic('Anchor'),150)
    item.purchased=True
    shop_state.restock_shop_item(item,game_state.player,rng=Rng(),relic_provider=lambda **kwargs:None)
    assert item.purchased and item.item.idstr=='Anchor'
