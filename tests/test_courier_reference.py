"""Reconstructed Courier loops with real original selector/gate/pricing methods."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.card_pools import definitions as cards, original_id, original_rarity
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import definitions as relics, make_relic
from rooms import shop_state
from tests.test_content_pool_reference import original_key, original_pool_state
from tests.test_special_card_reference import trace_rng
from utils.compatible_random import float32
from utils.random import get_random_relic
from utils.types import RarityType

ROWS=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/courier_reference.json.gz').read_bytes()))
COLORS={'RED':'ironclad','GREEN':'silent','BLUE':'defect','PURPLE':'watcher'}
BY_ORIGINAL={row['id']:key for key,row in relics().items()}


@pytest.mark.parametrize('row',ROWS)
def test_courier_original_component_results_calls_and_states(row,monkeypatch):
    merchant=cast(StreamRandom,get_rng('merchant'))
    merchant.seed(int(row.get('seed',20261110)))
    calls=[]
    original=merchant.random_float
    def floating(*args):
        value=original(*args)
        calls.append(['float',value] if not args else ['float_range',float32(args[0]),float32(args[1]),value])
        return value
    monkeypatch.setattr(merchant,'random_float',floating)
    if row['kind']=='colorless':
        game_state.player.namespace=COLORS[row['color']]
        game_state.ascension=row['ascension']
        game_state.player.relics=[make_relic('TheCourier')]+([make_relic('MembershipCard')] if row['membership'] else [])
        card_rng=cast(StreamRandom,get_rng('card'))
        card_rng.seed(int(row['seed'])+1)
        card_calls=trace_rng(card_rng,monkeypatch)
        old=cards()['Finesse' if row['old_tier']=='UNCOMMON' else 'Apotheosis'].make_card()
        item=shop_state.ShopItem('card',old,100)
        results=[]
        for _ in row['results']:
            shop_state.restock_shop_item(item,game_state.player)
            results.append([original_id(item.item),original_rarity(item.item).name,
                item.get_final_price_with_modifiers(row['ascension'],game_state)])
        assert results==row['results']
        assert card_calls==row['card_calls']
        state=card_rng.export_state()
        assert {key:state[key] for key in row['card_state']}==row['card_state']
    else:
        from rooms.shop import ShopRoom
        from rooms.treasure import TreasureRoom
        game_state.current_floor=row['floor']
        game_state.player.relics=[]
        game_state.current_room=ShopRoom() if row['shop'] else TreasureRoom()
        pools=game_state.relic_pools
        pools.remaining.update({tier:[BY_ORIGINAL[key] for key in values] for tier,values in row['before'].items()})
        tiers=iter(row['tiers'])
        # The original component receives an explicit tier schedule. SHOP-014
        # owns the existing project-vs-original tier probability discrepancy.
        monkeypatch.setattr(shop_state,'roll_relic_rarity',lambda rng:RarityType[next(tiers)])
        attempts=[]
        def provider(**kwargs):
            candidate=get_random_relic(**kwargs)
            attempts.append(original_key(candidate))
            return candidate
        item=shop_state.ShopItem('relic',make_relic('Anchor'),150)
        shop_state.restock_shop_item(item,game_state.player,relic_provider=provider)
        assert original_key(item.item)==row['result']
        assert attempts==row['attempts']
        assert original_pool_state(pools)==row['after']
        assert item.get_final_price_with_modifiers(20,has_the_courier=True,has_membership_card=row['membership'])==row['price']
    assert calls==row['merchant_calls']
    state=merchant.export_state()
    assert {key:state[key] for key in row['merchant_state']}==row['merchant_state']
