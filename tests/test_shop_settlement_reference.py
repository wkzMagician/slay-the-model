"""Actual original applyDiscount/getNewPrice and source post-purge price branch."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import make_relic
from rooms.shop import ShopRoom
from rooms.shop_pricing import compute_card_removal_price
from rooms.shop_state import ShopItem
from utils.compatible_random import float32, java_round_float

ROWS=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/shop_settlement_reference.json.gz').read_bytes()))


@pytest.mark.parametrize('row',ROWS)
def test_fixed_jar_settlement(row,monkeypatch):
    flags=dict(has_the_courier=row['courier'],has_membership_card=row['membership'],has_smiling_mask=row.get('mask',False))
    if row['kind']=='initial':
        game_state.ascension=row['ascension']
        game_state.player.relics=[make_relic(key) for key,enabled in [('TheCourier',row['courier']),('MembershipCard',row['membership']),('SmilingMask',row['mask'])] if enabled]
        room=ShopRoom()
        room.items=[ShopItem(kind,object(),row['base'],0.5 if kind=='card' and row['sale'] else 0) for kind in ('card','relic','potion')]
        room.prepare_prices()
        for item in room.items:
            assert item.get_final_price_with_modifiers(row['ascension'],**flags)==row[item.item_type]
        assert room.actual_card_removal_price==row['removal']
        room.on_shop_relic_purchased('MembershipCard')
        room.prepare_prices()
        for item in room.items:
            assert item.get_final_price_with_modifiers(row['ascension'],**flags)==row['dynamic_'+item.item_type]
        assert room.actual_card_removal_price==row['dynamic_removal']
    elif row['kind']=='removal':
        assert compute_card_removal_price(row['base'],**flags)==row['initial']
        assert compute_card_removal_price(row['base'],after_removal=True,**flags)==row['after_removal']
    else:
        rng=cast(StreamRandom,get_rng('merchant'))
        rng.seed(int(row['seed']))
        calls=[]
        draw=rng.random_float
        def floating(start,end):
            value=draw(start,end)
            calls.append(['float_range',float32(start),float32(end),value])
            return value
        monkeypatch.setattr(rng,'random_float',floating)
        for kind in ('relic','potion'):
            raw=java_round_float(float32(row['base']*rng.random_float(0.95,1.05)))
            item=ShopItem(kind,object(),raw)
            item.restocked=True
            assert item.get_final_price_with_modifiers(20,**flags)==row[kind]
        assert calls==row['calls']
        state=rng.export_state()
        assert {key:state[key] for key in row['state']}==row['state']
