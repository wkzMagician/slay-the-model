"""Shop role restriction and integer-tier protocol through native consumers."""
from collections import Counter
from types import SimpleNamespace
from typing import cast

import pytest

from actions.card_choice import ChooseObtainCardAction
from actions.misc import BuyItemAction
from actions.reward import AddRelicAction
from engine.card_pools import definitions, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import make_relic
from rooms import shop_state
from rooms.shop import ShopRoom
from utils.types import RarityType


def test_all_integer_rolls_have_original_distribution_and_bound():
    class Rng:
        value=0
        def random_int(self,bound):
            assert bound==99
            return self.value
    rng=Rng()
    counts=Counter()
    for value in range(100):
        rng.value=value
        counts[shop_state.roll_relic_rarity(rng)]+=1
    assert counts=={RarityType.COMMON:48,RarityType.UNCOMMON:34,RarityType.RARE:18}


@pytest.mark.parametrize('player',[None,SimpleNamespace(relics=[]),SimpleNamespace(namespace='',relics=[])])
def test_default_shop_namespace_compatibility(player):
    assert shop_state.build_card_namespaces(player)==['ironclad']


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension',[0,20])
@pytest.mark.parametrize('shard',[False,True])
@pytest.mark.parametrize('seed',[0,1,42,20261111])
def test_normal_inventory_and_three_colored_purchases_keep_role(role,ascension,shard,seed,monkeypatch):
    player=game_state.player
    player.namespace=role
    player.relics=[]
    game_state.ascension=ascension
    game_state.current_floor=5
    AddRelicAction(make_relic('TheCourier')).execute()
    if shard:
        AddRelicAction(make_relic('PrismaticShard')).execute()
    player.gold=10000
    for name in ('card','merchant','potion'):
        cast(StreamRandom,get_rng(name)).seed(seed)
    merchant=cast(StreamRandom,get_rng('merchant'))
    integer=merchant.random_int
    calls=[]
    def draw(*args):
        calls.append(args)
        return integer(*args)
    monkeypatch.setattr(merchant,'random_int',draw)
    room=ShopRoom()
    room.init()
    assert calls.count((99,))==2
    assert len(room.items)==13
    assert all(definitions()[original_id(item.item)].namespace==role for item in room.items[:5])
    assert all(definitions()[original_id(item.item)].namespace=='colorless' for item in room.items[5:7])
    assert shop_state.build_card_namespaces(player)==[role]
    item=room.items[0]
    count=len(player.card_manager.get_pile('deck'))
    for _ in range(3):
        menu=room._build_shop_menu()
        action=next(action for option in menu.options for action in option.actions if isinstance(action,BuyItemAction) and action.shop_item is item)
        price=item.get_final_price_with_modifiers(ascension,game_state)
        gold=player.gold
        action.execute()
        assert gold-player.gold==price
        assert definitions()[original_id(item.item)].namespace==role
        assert not item.purchased and item.quoted_price is not None
    assert len(player.card_manager.get_pile('deck'))==count+3


@pytest.mark.parametrize('role',['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('shard',[False,True])
def test_combat_reward_keeps_prismatic_scope(role,shard,monkeypatch):
    import actions.card_choice as choices
    game_state.player.namespace=role
    game_state.player.relics=[make_relic('PrismaticShard')] if shard else []
    cast(StreamRandom,get_rng('card')).seed(42)
    original=choices.get_card_reward_options
    observed=[]
    def provider(**kwargs):
        cards=original(**kwargs)
        observed.append((kwargs['namespaces'],cards))
        return cards
    monkeypatch.setattr(choices,'get_card_reward_options',provider)
    ChooseObtainCardAction(namespace=role).execute()
    assert observed[0][0]==(None if shard else [role])
    assert len(observed[0][1])==3
    namespaces={definitions()[original_id(card)].namespace for card in observed[0][1]}
    if shard:
        assert namespaces-{role}
    else:
        assert namespaces=={role}
