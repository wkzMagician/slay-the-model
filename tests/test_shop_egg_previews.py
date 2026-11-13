"""Real inventory, relic purchase and Courier preview entry regressions."""
from itertools import combinations
from typing import cast

import pytest

from actions.misc import BuyItemAction
from cards.base import Card
from engine.card_pools import definitions, original_id
from engine.game_state import game_state
from engine.random_streams import DOMAINS, StreamRandom, get_rng
from relics.pools import make_relic
from rooms import shop_state
from rooms.shop import ShopRoom
from utils.types import CardType

EGGS={'MoltenEgg':'ATTACK','ToxicEgg':'SKILL','FrozenEgg':'POWER'}
HELD=[list(items) for count in range(4) for items in combinations(EGGS,count)]


def states():
    return {name:cast(StreamRandom,get_rng(name)).export_state() for name in DOMAINS}


def buy(room,item):
    menu=room._build_shop_menu()
    action=next(action for option in menu.options for action in option.actions
                if isinstance(action,BuyItemAction) and action.shop_item is item)
    before=game_state.player.gold
    price=item.get_final_price_with_modifiers(game_state.ascension,game_state)
    sold=item.item
    action.execute()
    assert before-game_state.player.gold==price
    return sold


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('held',HELD)
@pytest.mark.parametrize('seed',[0,1,42])
def test_real_initial_inventory_previews_each_card_without_rng(role,ascension,held,seed,monkeypatch):
    player=game_state.player
    player.namespace=role
    player.relics=[make_relic(key) for key in held]
    game_state.ascension=ascension
    game_state.current_floor=5
    for name in ('card','merchant','potion'):
        cast(StreamRandom,get_rng(name)).seed(seed)
    observations=[]
    original=shop_state.preview_shop_card
    def observe(card,relics):
        before=states()
        kind=definitions()[original_id(card)].type
        expected=int(kind in {EGGS[key] for key in held} and card.can_upgrade())
        original(card,relics)
        assert states()==before
        assert card.upgrade_level==expected
        observations.append(card)
    monkeypatch.setattr(shop_state,'preview_shop_card',observe)
    room=ShopRoom()
    room.init()
    assert len(room.items)==13 and len(observations)==7
    assert all(observations[index] is room.items[index].item for index in range(7))
    before=states()
    levels=[item.item.upgrade_level for item in room.items[:7]]
    for _ in range(3): room._build_shop_menu()
    assert levels==[item.item.upgrade_level for item in room.items[:7]]
    assert states()==before


@pytest.mark.parametrize('egg,card_id,attribute,value',[
    ('MoltenEgg','Anger','damage',8),('ToxicEgg','Shrug It Off','block',11),
    ('FrozenEgg','Corruption','cost',2),('MoltenEgg','Searing Blow','damage',16),
])
def test_preview_numeric_effect_name_and_purchase_identity(egg,card_id,attribute,value):
    player=game_state.player
    player.relics=[make_relic(egg)]
    player.gold=10000
    card=definitions()[card_id].make_card()
    before=states()
    shop_state.preview_shop_card(card,player.relics)
    assert states()==before
    assert card.upgrade_level==1 and getattr(card,attribute)==value
    assert '+' in str(card.display_name)
    item=shop_state.ShopItem('card',card,101)
    room=ShopRoom()
    room.items=[item]
    game_state.current_room=room
    room.prepare_prices()
    quote=item.get_final_price()
    for _ in range(3):
        shop_state.preview_shop_card(card,player.relics)
        room._build_shop_menu()
    assert item.get_final_price()==quote
    sold=buy(room,item)
    assert sold is card and card.upgrade_level==1 and getattr(card,attribute)==value
    assert any(value is card for value in player.card_manager.get_pile('deck'))


@pytest.mark.parametrize('egg,expected',[('ToxicEgg',1),('FrozenEgg',0)])
def test_preview_uses_original_type_for_flame_barrier(egg,expected):
    card=definitions()['Flame Barrier'].make_card()
    shop_state.preview_shop_card(card,[make_relic(egg)])
    assert card.upgrade_level==expected


def test_extension_card_uses_its_own_type_and_upgrades_once():
    class ExtensionCard(Card):
        card_type=CardType.SKILL
        upgrade_limit=99
        base_cost=2
        upgrade_cost=1
    card=ExtensionCard()
    for _ in range(3): shop_state.preview_shop_card(card,[make_relic('ToxicEgg')])
    assert card.upgrade_level==1 and card.cost==1


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('egg',list(EGGS))
@pytest.mark.parametrize('courier',[False,True])
def test_buy_egg_upgrades_both_rows_then_buy_previewed_cards(role,ascension,egg,courier):
    player=game_state.player
    player.namespace=role
    player.relics=[make_relic('TheCourier')] if courier else []
    player.gold=10000
    game_state.ascension=ascension
    game_state.current_floor=5
    records=definitions()
    def own(kind):
        return next(row.make_card() for row in records.values()
                    if row.namespace==role and row.type==kind and row.rarity in ('COMMON','UNCOMMON','RARE'))
    colored=[own(kind) for kind in ('ATTACK','ATTACK','SKILL','SKILL','POWER')]
    target={'MoltenEgg':'Flash of Steel','ToxicEgg':'Finesse','FrozenEgg':'Panache'}[egg]
    neutral=[records[target].make_card(),records['Apotheosis'].make_card()]
    room=ShopRoom()
    room.items=[shop_state.ShopItem('card',card,101) for card in colored+neutral]
    relic_item=shop_state.ShopItem('relic',make_relic(egg),250)
    room.items.append(relic_item)
    game_state.current_room=room
    room.prepare_prices()
    prices=[item.quoted_price for item in room.items[:7]]
    sold=buy(room,relic_item)
    assert sold.idstr in game_state.obtained_relics
    assert prices==[item.quoted_price for item in room.items[:7]]
    for item in room.items[:7]:
        assert item.item.upgrade_level==int(records[original_id(item.item)].type==EGGS[egg])
    for _ in range(3): room._build_shop_menu()
    matching=[item for item in room.items[:7] if records[original_id(item.item)].type==EGGS[egg]]
    for item in (matching[0],room.items[5]):
        card=item.item
        assert card.upgrade_level==1
        buy(room,item)
        assert card.upgrade_level==1
        assert any(value is card for value in player.card_manager.get_pile('deck'))


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('egg',list(EGGS))
@pytest.mark.parametrize('colorless',[False,True])
@pytest.mark.parametrize('seed',[0,42])
def test_real_courier_replacement_is_previewed_before_price(role,ascension,egg,colorless,seed,monkeypatch):
    player=game_state.player
    player.namespace=role
    player.relics=[make_relic('TheCourier'),make_relic(egg)]
    player.gold=10000
    game_state.ascension=ascension
    game_state.current_floor=5
    cast(StreamRandom,get_rng('card')).seed(seed)
    cast(StreamRandom,get_rng('merchant')).seed(seed)
    records=definitions()
    if colorless:
        key={'MoltenEgg':'Flash of Steel','ToxicEgg':'Finesse','FrozenEgg':'Panache'}[egg]
        old=records[key].make_card()
    else:
        old=next(row.make_card() for row in records.values() if row.namespace==role
                 and row.type==EGGS[egg] and row.rarity in ('COMMON','UNCOMMON','RARE'))
    shop_state.preview_shop_card(old,player.relics)
    item=shop_state.ShopItem('card',old,101)
    room=ShopRoom()
    room.items=[item]
    game_state.current_room=room
    events=[]
    original_preview=shop_state.preview_shop_card
    original_price=shop_state._card_price
    def preview(card,relics):
        before=states()
        expected=int(records[original_id(card)].type==EGGS[egg] and card.can_upgrade())
        original_preview(card,relics)
        assert card.upgrade_level==expected
        assert states()==before
        events.append(('preview',card))
    def price(rarity,rng,**kwargs):
        assert events[-1][0]=='preview'
        events.append(('price',rarity))
        return original_price(rarity,rng,**kwargs)
    monkeypatch.setattr(shop_state,'preview_shop_card',preview)
    monkeypatch.setattr(shop_state,'_card_price',price)
    for _ in range(2):
        sold=buy(room,item)
        assert sold.upgrade_level<=1
        assert item.item is not sold and not item.purchased
    assert [value[0] for value in events]==['preview','price','preview','price']


def test_sold_card_is_excluded_from_later_egg_inventory_refresh():
    player=game_state.player
    player.relics=[]
    player.gold=10000
    card=definitions()['Searing Blow'].make_card()
    old=shop_state.ShopItem('card',card,100)
    egg=shop_state.ShopItem('relic',make_relic('MoltenEgg'),250)
    room=ShopRoom()
    room.items=[old,egg]
    game_state.current_room=room
    buy(room,old)
    assert old.purchased and card.upgrade_level==0
    buy(room,egg)
    assert card.upgrade_level==0

def test_initial_prices_precede_preview_and_sale_follows_all_previews(monkeypatch):
    player=game_state.player
    player.relics=[make_relic(key) for key in EGGS]
    prepared=iter(definitions()[key].make_card() for key in [
        'Anger','Cleave','Shrug It Off','True Grit','Corruption','Finesse','Panache'])
    events=[]
    original_preview=shop_state.preview_shop_card
    original_price=shop_state._card_price
    def price(*args,**kwargs):
        events.append('price')
        return original_price(*args,**kwargs)
    def preview(card,relics):
        events.append('preview')
        return original_preview(card,relics)
    rng=cast(StreamRandom,get_rng('merchant'))
    integer=rng.random_int
    def draw(*args):
        if args==(0,4): events.append('sale')
        return integer(*args)
    monkeypatch.setattr(shop_state,'_card_price',price)
    monkeypatch.setattr(shop_state,'preview_shop_card',preview)
    monkeypatch.setattr(rng,'random_int',draw)
    shop_state.generate_shop_items(player,card_provider=lambda **kwargs:next(prepared))
    assert events==['price','preview']*7+['sale']
