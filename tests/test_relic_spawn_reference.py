"""Actual original canSpawn methods and key draws against explicit prepared state."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.reward import AddEliteRelicAction
from engine.card_pools import definitions as card_definitions
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import definitions, make_relic
from tests.test_content_pool_reference import original_key, original_pool_state
from utils.random import get_random_relic
from utils.types import RarityType

REFERENCE = json.loads(gzip.decompress((Path(__file__).parent/'fixtures/relic_spawn_reference.json.gz').read_bytes()))
BY_ORIGINAL = {row['id']:key for key,row in definitions().items()}


@pytest.mark.parametrize('row', REFERENCE)
def test_actual_original_spawn_and_draw_contract(row, monkeypatch):
    from rooms.shop import ShopRoom
    from rooms.treasure import TreasureRoom
    game_state.player.namespace = row['role']
    game_state.ascension = row['ascension']
    game_state.current_floor = row['floor']
    # Preserve the explicit absolute floor when preparing independent act cases.
    game_state.current_act = row['act']
    game_state.floor_in_act = row['floor'] - sum(
        game_state._get_max_floor_in_act(act) for act in range(1,row['act'])
    )
    assert game_state.current_floor == row['floor']
    game_state.current_room = ShopRoom() if row['shop'] else TreasureRoom()
    game_state.player.relics = [make_relic(BY_ORIGINAL[key]) for key in row['held']]
    deck = [card_definitions()[key].make_card() for key in row['deck']]
    if row['upgraded']:
        for card in deck:
            card.upgrade()
    game_state.player.card_manager.piles['deck'] = deck
    rng = cast(StreamRandom,get_rng('relic'))
    rng.seed(20261108)
    if row['category'] != 'draw':
        assert make_relic(BY_ORIGINAL[row['key']]).can_spawn() == row['allowed']
    else:
        pools = game_state.relic_pools
        pools.remaining.update({tier:[] for tier in ('COMMON','UNCOMMON','RARE','SHOP','BOSS')})
        pools.remaining[row['tier']] = [BY_ORIGINAL[key] for key in row['pool']]
        if row['non_campfire']:
            # The original component receives an already chosen tier. Fix only that
            # outer roll here, leaving production qualification and retries intact.
            monkeypatch.setattr(rng,'randint',lambda *args:99)
            previous = len(game_state.player.relics)
            AddEliteRelicAction(non_campfire=True).execute()
            relic = game_state.player.relics[previous]
        else:
            relic = get_random_relic(rarities=[RarityType[row['tier']]],from_end=row['shop'])
        assert original_key(relic) == row['result']
        assert original_pool_state(pools) == row['after']
    assert row['calls'] == []
    state = rng.export_state()
    assert {key:state[key] for key in row['state']} == row['state']
