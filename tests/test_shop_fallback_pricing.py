"""Normal shop fallback, finite exhaustion, actual-tier pricing and purchase regressions."""
from types import SimpleNamespace
from typing import cast

import pytest

from actions.misc import BuyItemAction
from engine.card_pools import current_pools, definitions, original_id, original_rarity
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import make_relic
from rooms import shop_state
from rooms.shop import ShopRoom
from utils.compatible_random import float32
from utils.types import CardType, RarityType


@pytest.mark.parametrize('first,available,expected',[
    (RarityType.COMMON,RarityType.UNCOMMON,[RarityType.COMMON,RarityType.UNCOMMON]),
    (RarityType.COMMON,RarityType.RARE,[RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE]),
    (RarityType.UNCOMMON,RarityType.RARE,[RarityType.UNCOMMON,RarityType.RARE]),
    (RarityType.RARE,RarityType.UNCOMMON,[RarityType.RARE,RarityType.UNCOMMON]),
])
def test_fallback_checks_each_tier_without_reroll(first,available,expected,monkeypatch):
    calls=[]
    roll_calls=[]
    def roll(rng):
        roll_calls.append(1)
        return first
    monkeypatch.setattr(shop_state,'roll_card_rarity',roll)
    def provider(**kwargs):
        kind=kwargs['card_types'][0]
        if kind != CardType.POWER:
            return SimpleNamespace(idstr=f'{kind}-{len(roll_calls)}',namespace='ironclad')
        calls.append(kwargs['rarities'][0])
        return definitions()['Corruption' if available==RarityType.RARE else 'Inflame'].make_card() if calls[-1]==available else None
    result=shop_state.generate_colored_cards(game_state.player,card_provider=provider)
    assert len(result)==5
    assert len(roll_calls)==5
    assert calls==expected
    assert original_rarity(result[-1])==available


def test_real_empty_tiers_do_not_consume_selection_rng(monkeypatch):
    pools=current_pools()
    pools.current[('ironclad','UNCOMMON')]=[]
    rng=cast(StreamRandom,get_rng('card'))
    counter=rng.counter
    monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng:RarityType.COMMON)
    cards=shop_state.generate_colored_cards(game_state.player)
    assert len(cards)==5
    assert original_rarity(cards[-1])==RarityType.RARE
    # Every nonempty selection consumes a roll, including any duplicate retries.
    assert rng.counter-counter>=5
    calls=[]
    exhausted=shop_state._shop_card(CardType.POWER,RarityType.COMMON,['ironclad'],lambda **kwargs:calls.append(kwargs['rarities'][0]))
    assert exhausted is None
    assert calls==[RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE]


@pytest.mark.parametrize('requested,actual',[(RarityType.COMMON,'Ginger'),(RarityType.UNCOMMON,'Circlet')])
def test_initial_relic_price_uses_obtained_tier(requested,actual,monkeypatch):
    class Rng:
        def random_float(self,start,end): return 1.0
        def randint(self,low,high): return 0
    monkeypatch.setattr(shop_state,'generate_colored_cards',lambda **kwargs:[])
    monkeypatch.setattr(shop_state,'generate_colorless_cards',lambda **kwargs:[])
    monkeypatch.setattr(shop_state,'roll_relic_rarity',lambda rng:requested)
    monkeypatch.setattr(shop_state,'roll_potion_rarity',lambda rng:RarityType.COMMON)
    from relics.global_relics.special import Circlet
    relic=Circlet() if actual=='Circlet' else make_relic(actual)
    items=shop_state.generate_shop_items(game_state.player,rng=Rng(),relic_provider=lambda **kwargs:relic,
        potion_provider=lambda **kwargs:SimpleNamespace(rarity=RarityType.COMMON))
    assert [item.base_price for item in items[:3]]==[300 if actual=='Ginger' else 400]*3


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('shard',[False,True])
@pytest.mark.parametrize('seed',range(10))
def test_real_shop_always_has_all_card_slots(role,ascension,shard,seed):
    game_state.player.namespace=role
    game_state.player.relics=[make_relic('PrismaticShard')] if shard else []
    game_state.ascension=ascension
    game_state.current_floor=5
    for name in ('card','merchant','potion'):
        cast(StreamRandom,get_rng(name)).seed(seed)
    room=ShopRoom()
    room.init()
    assert len(room.items)==13
    cards=[item.item for item in room.items[:5]]
    assert [definitions()[original_id(card)].type for card in cards]==['ATTACK','ATTACK','SKILL','SKILL','POWER']
    assert sum(item.discount==0.5 for item in room.items)==1
    assert all(isinstance(item.base_price,int) for item in room.items)


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('membership',[False,True])
def test_actual_buy_twice_restock_power_and_defer_card_rounding(role,ascension,membership,monkeypatch):
    player=game_state.player
    player.namespace=role
    player.relics=[make_relic('TheCourier')]+([make_relic('MembershipCard')] if membership else [])
    player.gold=10000
    game_state.ascension=ascension
    game_state.current_floor=5
    room=ShopRoom()
    room.init()
    item=room.items[4]
    deck_before=len(player.card_manager.get_pile('deck'))
    # Force the documented missing COMMON power tier through the real purchase
    # and restock entry; all candidate selection and pricing remain production.
    monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng:RarityType.COMMON)
    for _ in range(2):
        before=player.gold
        # BuyItemAction's existing ascension_level input is tracked by SHOP-002.
        price=item.get_final_price_with_modifiers(getattr(game_state,'ascension_level',0),game_state)
        BuyItemAction(item,4).execute()
        assert before-player.gold==price
        assert definitions()[original_id(item.item)].type=='POWER'
        assert original_rarity(item.item)==RarityType.UNCOMMON
        assert item.card_restock and not item.purchased
        raw=float32(item.base_price*float32(0.8))
        if membership:
            raw=float32(raw*float32(0.5))
        assert item.get_final_price_with_modifiers(ascension,game_state)==int(raw)
    assert len(player.card_manager.get_pile('deck'))==deck_before+2


def test_older_item_without_restock_marker_retains_initial_price_behavior():
    item=shop_state.ShopItem('card',definitions()['Anger'].make_card(),50)
    del item.card_restock
    assert item.get_final_price()==50
