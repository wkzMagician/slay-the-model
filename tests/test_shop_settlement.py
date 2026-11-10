"""Normal menu/payment, membership acquisition and removal phase regressions."""
import pytest

from actions.misc import BuyItemAction
from engine.card_pools import definitions
from engine.game_state import game_state
from relics.pools import make_relic
from rooms.shop import ShopRoom
from rooms.shop_pricing import compute_shop_price
from rooms.shop_state import ShopItem
from utils.compatible_random import float32, java_round_float


def held(courier,membership):
    return [make_relic(key) for key,enabled in [('TheCourier',courier),('MembershipCard',membership)] if enabled]


def test_initial_sale_precedes_ascension_and_rounding():
    assert compute_shop_price(51,16,discount=0.5,item_type='card')==28
    assert compute_shop_price(75,has_membership_card=True,item_type='potion')==38


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,15,16,20])
@pytest.mark.parametrize('courier,membership',[(False,False),(True,False),(False,True),(True,True)])
@pytest.mark.parametrize('kind',['card','relic','potion'])
def test_menu_affordability_and_payment_use_one_quote(role,ascension,courier,membership,kind):
    game_state.player.namespace=role
    game_state.ascension=ascension
    game_state.player.relics=held(courier,membership)
    if kind=='card':
        value=definitions()['Anger'].make_card()
    elif kind=='relic':
        value=make_relic('Anchor')
    else:
        from potions.global_potions import FirePotion
        value=FirePotion()
    item=ShopItem(kind,value,101,0.5 if kind=='card' else 0)
    room=ShopRoom()
    room.items=[item]
    game_state.current_room=room
    # Prepared base price isolates settlement from generation RNG and tier rules.
    expected=50 if kind=='card' else 101
    if ascension>=16: expected=java_round_float(float32(expected*float32(1.1)))
    if courier: expected=java_round_float(float32(expected*float32(0.8)))
    if membership: expected=java_round_float(float32(expected*float32(0.5)))
    game_state.player.gold=expected-1
    menu=room._build_shop_menu()
    assert not any(isinstance(action,BuyItemAction) and action.shop_item is item for option in menu.options for action in option.actions)
    game_state.player.gold=expected
    menu=room._build_shop_menu()
    action=next(action for option in menu.options for action in option.actions if isinstance(action,BuyItemAction) and action.shop_item is item)
    assert item.get_final_price_with_modifiers(ascension,game_state)==expected
    action.execute()
    assert game_state.player.gold==0


@pytest.mark.parametrize('ascension',[0,15,16,20])
@pytest.mark.parametrize('courier',[False,True])
def test_buy_membership_discounts_existing_quotes_once(ascension,courier):
    game_state.ascension=ascension
    game_state.player.relics=held(courier,False)
    game_state.player.gold=10000
    room=ShopRoom()
    member=ShopItem('relic',make_relic('MembershipCard'),150)
    existing=ShopItem('card',definitions()['Anger'].make_card(),104.8)
    existing.card_restock=True
    existing.restocked=True
    room.items=[member,existing]
    game_state.current_room=room
    room.prepare_prices()
    old_price=existing.get_final_price()
    member_price=member.get_final_price()
    BuyItemAction(member,0).execute()
    assert game_state.player.gold==10000-member_price
    expected=java_round_float(float32(old_price*float32(0.5)))
    assert existing.get_final_price()==expected
    if courier: assert expected==42
    assert room.actual_card_removal_price==38
    for _ in range(3):
        room._build_shop_menu()
        assert existing.get_final_price()==expected


@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('mask',[False,True])
def test_removal_quote_after_purchase_and_on_next_visit(ascension,mask,monkeypatch):
    from actions.card import ChooseRemoveCardAction
    monkeypatch.setattr(ChooseRemoveCardAction,'execute',lambda self:None)
    game_state.ascension=ascension
    game_state.player.relics=held(True,True)+([make_relic('SmilingMask')] if mask else [])
    game_state.player.gold=1000
    room=ShopRoom()
    game_state.current_room=room
    menu=room._build_shop_menu()
    action=next(action for option in menu.options for action in option.actions if isinstance(action,BuyItemAction) and action.shop_item.item_type=='card_removal')
    assert room.actual_card_removal_price==(50 if mask else 38)
    action.execute()
    assert game_state.player.gold==1000-(50 if mask else 38)
    assert room.card_removal_used
    assert room.actual_card_removal_price==(50 if mask else 40)
    room.leave()
    next_room=ShopRoom()
    next_room.card_removal_price=game_state.card_removal_price
    next_room.prepare_prices()
    assert next_room.actual_card_removal_price==50


def test_legacy_item_without_new_quote_fields_still_prices():
    item=ShopItem('potion',object(),75)
    del item.quoted_price
    del item.restocked
    assert item.get_final_price_with_modifiers(20,has_membership_card=True)==42
