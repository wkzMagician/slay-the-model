"""Actual original Egg2 hooks compared with preview and real obtain processing."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.card import AddCardAction
from engine.card_pools import definitions
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import make_relic
from rooms.shop_state import preview_shop_card

ROWS=json.loads(gzip.decompress((Path(__file__).parent/'fixtures/egg_preview_reference.json.gz').read_bytes()))


@pytest.mark.parametrize('row',ROWS)
def test_original_egg_preview_and_obtain_guards(row):
    player=game_state.player
    player.relics=[make_relic(key) for key in row['held']]
    card=definitions()[row['card']].make_card()
    card.upgrade_level=row['initial_level']
    card.upgradeable=row['available']
    card.upgrade_limit=99 if row['multi'] else 1
    for name,seed in [('card',11),('merchant',12)]:
        cast(StreamRandom,get_rng(name)).seed(seed)
    levels=[]
    for _ in range(2):
        preview_shop_card(card,player.relics)
        levels.append(card.upgrade_level)
    AddCardAction(card=card,dest_pile='deck',source='shop').execute()
    levels.append(card.upgrade_level)
    assert any(value is card for value in player.card_manager.get_pile('deck'))
    preview_shop_card(card,player.relics)
    levels.append(card.upgrade_level)
    assert levels==row['levels']
    assert row['card_calls']==row['merchant_calls']==[]
    for name in ('card','merchant'):
        state=cast(StreamRandom,get_rng(name)).export_state()
        assert {key:state[key] for key in row[name+'_state']}==row[name+'_state']
