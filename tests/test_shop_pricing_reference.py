"""Prepared JAR pricing components and previously deferred power-slot cases."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.card_pools import definitions, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from rooms import shop_state
from tests.test_shop_card_reference import COLORS
from tests.test_special_card_reference import trace_rng
from utils.compatible_random import float32
from utils.types import RarityType

FIXTURES=Path(__file__).parent/'fixtures'
FALLBACK=json.loads(gzip.decompress((FIXTURES/'shop_card_fallback_reference.json.gz').read_bytes()))
PRICES=json.loads(gzip.decompress((FIXTURES/'shop_price_reference.json.gz').read_bytes()))


@pytest.mark.parametrize('row',FALLBACK)
def test_previously_deferred_power_slot_ids_calls_and_state(row,monkeypatch):
    game_state.player.namespace=COLORS[row['color']]
    game_state.player.relics=[]
    game_state.ascension=row['ascension']
    game_state.card_rarity_offset=row['offset']
    rng=cast(StreamRandom,get_rng('card'))
    rng.seed(int(row['seed']))
    calls=trace_rng(rng,monkeypatch)
    cards=shop_state.generate_colored_cards(game_state.player)+shop_state.generate_colorless_cards()
    assert row['power_fallback']
    assert [original_id(card) for card in cards]==row['cards']
    assert calls==row['calls']
    state=rng.export_state()
    assert {key:state[key] for key in row['state']}==row['state']
    assert game_state.card_rarity_offset==row['after_offset']


@pytest.mark.parametrize('row',PRICES)
def test_prices_and_merchant_state_against_fixed_jar(row,monkeypatch):
    rarity=RarityType[row['tier']]
    functions={'colored':shop_state.get_card_price,'colorless':shop_state.get_colorless_card_price,
               'potion':shop_state.get_potion_price,'relic':shop_state.get_relic_price}
    if row['mode']=='grid':
        class GridRng:
            quantile=0.0
            def random_float(self,start,end):
                start,end=float32(start),float32(end)
                return float32(start+float32(self.quantile*float32(end-start)))
        grid=GridRng()
        actual=[]
        for value in row['quantiles']:
            grid.quantile=value
            actual.append(functions[row['kind']](rarity,grid))
        assert actual==row['prices']
        return
    rng=cast(StreamRandom,get_rng('merchant'))
    rng.seed(int(row['seed']))
    calls=[]
    original=rng.random_float
    def draw(start,end):
        value=original(start,end)
        calls.append(['float_range',float32(start),float32(end),value])
        return value
    monkeypatch.setattr(rng,'random_float',draw)
    if row['mode']=='restock':
        keys={'colored':{'COMMON':'Anger','UNCOMMON':'Inflame','RARE':'Corruption'},
              'colorless':{'UNCOMMON':'Finesse','RARE':'Apotheosis'}}
        definition=definitions()[keys[row['kind']][row['tier']]]
        item=shop_state.ShopItem('card',definition.make_card(),100)
        # Original setPrice receives an already selected card. Fix only the outer
        # rarity/candidate inputs while running production restock price handling.
        monkeypatch.setattr(shop_state,'roll_card_rarity',lambda rng:rarity)
        actual=[]
        for _ in row['prices']:
            shop_state.restock_shop_item(item,game_state.player,rng=rng,card_provider=lambda **kwargs:definition.make_card())
            actual.append(item.get_final_price_with_modifiers(ascension_level=20,
                has_the_courier=row['courier'],has_membership_card=row['membership']))
    else:
        actual=[functions[row['kind']](rarity,rng) for _ in row['prices']]
    assert actual==row['prices']
    assert calls==row['calls']
    state=rng.export_state()
    assert {key:state[key] for key in row['state']}==row['state']
