"""Actual original merchant tier/init methods and reconstructed selection loops."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.card_pools import definitions as cards, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import definitions as relics, make_relic
from rooms import shop_state
from rooms.shop import ShopRoom
from tests.test_content_pool_reference import original_key, original_pool_state
from tests.test_special_card_reference import trace_rng
from utils.compatible_random import float32
from utils.random import get_random_potion, get_random_relic
from utils.types import RarityType

ROWS=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/merchant_protocol_reference.json.gz').read_bytes()))
COLORS={'RED':'ironclad','GREEN':'silent','BLUE':'defect','PURPLE':'watcher'}
BY_ORIGINAL={row['id']:key for key,row in relics().items()}


@pytest.mark.parametrize('row',ROWS)
def test_original_merchant_protocol(row,monkeypatch):
    if row['kind']=='grid':
        calls=[]
        class FixedRng:
            def random_int(self,bound):
                calls.append(['int',bound,row['roll']])
                return row['roll']
        assert shop_state.roll_relic_rarity(FixedRng()).name==row['tier']
        assert calls==row['calls']
        return
    if row['kind']=='cards':
        game_state.player.namespace=COLORS[row['color']]
        game_state.player.relics=[make_relic('PrismaticShard')] if row['shard'] else []
        game_state.ascension=row['ascension']
        game_state.card_rarity_offset=row['offset']
        game_state.current_room=ShopRoom()
        rng=cast(StreamRandom,get_rng('card'))
        rng.seed(int(row['seed']))
        calls=trace_rng(rng,monkeypatch)
        chosen=shop_state.generate_colored_cards(game_state.player)+shop_state.generate_colorless_cards()
        assert [original_id(card) for card in chosen]==row['cards']
        assert calls==row['calls']
        assert game_state.card_rarity_offset==row['after_offset']
        state=rng.export_state()
        assert {key:state[key] for key in row['state']}==row['state']
        return
    from rooms.treasure import TreasureRoom
    game_state.current_floor=row['floor']
    game_state.ascension=row['ascension']
    game_state.current_room=ShopRoom() if row['shop'] else TreasureRoom()
    game_state.player.relics=[]
    game_state.obtained_relics.clear()
    game_state.player.card_manager.piles['deck']=[]
    pools=game_state.relic_pools
    pools.remaining.update({tier:[BY_ORIGINAL[key] for key in values] for tier,values in row['before'].items()})
    rng=cast(StreamRandom,get_rng('merchant'))
    rng.seed(int(row['seed']))
    calls=[]
    integer,floating=rng.random_int,rng.random_float
    def draw(bound):
        value=integer(bound)
        calls.append(['int',bound,value])
        return value
    def multiplier(low,high):
        value=floating(low,high)
        calls.append(['float_range',float32(low),float32(high),value])
        return value
    monkeypatch.setattr(rng,'random_int',draw)
    monkeypatch.setattr(rng,'random_float',multiplier)
    if row['kind']=='initial':
        boundary={}
        def potion_provider(**kwargs):
            if not boundary:
                boundary.update(calls=list(calls),state=rng.export_state())
            return get_random_potion(**kwargs)
        # Empty card candidates place merchantRng at the initRelics boundary.
        # The potion observer forwards real selection and captures its start.
        items=shop_state.generate_shop_items(game_state.player,
            card_provider=lambda **kwargs:None,potion_provider=potion_provider)
        assert [[original_key(item.item),item.base_price] for item in items if item.item_type=='relic']==row['items']
        assert boundary['calls']==row['calls']
        assert {key:boundary['state'][key] for key in row['state']}==row['state']
    else:
        attempts=[]
        def provider(**kwargs):
            value=get_random_relic(**kwargs)
            attempts.append([kwargs['rarities'][0].name,original_key(value)])
            return value
        item=shop_state.ShopItem('relic',make_relic('Anchor'),150)
        shop_state.restock_shop_item(item,game_state.player,relic_provider=provider)
        assert attempts==row['attempts']
        assert original_key(item.item)==row['result']
        assert item.get_final_price_with_modifiers(20,has_the_courier=True,
            has_membership_card=row['membership'])==row['price']
        assert calls==row['calls']
        state=rng.export_state()
        assert {key:state[key] for key in row['state']}==row['state']
    assert original_pool_state(pools)==row['after']
