"""Actual fixed-JAR pool methods, using explicit metadata/gate preparation."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from relics.pools import RelicPools, definitions
from utils.compatible_random import GameRandom
from utils.random import get_random_potion

REFERENCE = json.loads(gzip.decompress((Path(__file__).parent/'fixtures/content_pool_reference.json.gz').read_bytes()))
TIERS = ('COMMON','UNCOMMON','RARE','SHOP','BOSS')


def original_key(relic):
    return getattr(relic,'_original_relic_id', 'Red Circlet' if relic.idstr == 'RedCirclet' else relic.idstr)


def original_pool_state(pools):
    rows = definitions()
    result = {}
    for tier in TIERS:
        remaining = pools.remaining[tier]
        assert remaining is not None
        result[tier] = [rows[key]['id'] for key in remaining]
    return result


@pytest.mark.parametrize('row', REFERENCE, ids=lambda row:'-'.join(str(row.get(key,'')) for key in ('kind','role','seed','tier','from_end','scenario','mode')))
def test_fixed_jar_content_pool_results_calls_and_final_state(row, monkeypatch):
    from utils.types import RarityType
    game_state.player.namespace = row['role']
    game_state.player.relics = []
    if row['kind'] == 'potion_draw':
        rng = cast(StreamRandom, get_rng('potion'))
        rng.seed(int(row['seed']))
        calls = []
        original = rng.random_int
        def draw(start, end=None):
            value = original(start, end)
            calls.append(['int',start,value] if end is None else ['int_range',start,end,value])
            return value
        monkeypatch.setattr(rng,'random_int',draw)
        mode = row['mode']
        rarities = None if mode in ('uniform','weighted') else [RarityType[mode.removeprefix('limited_')]]
        results = []
        for _ in range(5):
            potion = get_random_potion([row['role']],rarities,uniform=mode == 'uniform',limited=mode.startswith('limited_'))
            assert potion is not None
            results.append(potion._original_potion_id)
        assert results == row['results']
        assert calls == row['calls']
        state = rng.export_state()
    else:
        parent = GameRandom(int(row['seed']))
        seeds = {tier.lower():parent.random_long() for tier in TIERS}
        calls = [['long',str(value)] for value in seeds.values()]
        pools = RelicPools(seeds)
        for tier in TIERS:
            pools.initialize(tier)
        if row['kind'] == 'initialize':
            assert original_pool_state(pools) == row['pools']
        else:
            by_original = {value['id']:key for key,value in definitions().items()}
            pools.remaining.update({tier:[by_original[value] for value in row['before'][tier]] for tier in TIERS})
            import relics.pools as module
            make = module.make_relic
            def prepared_relic(key):
                relic = make(key)
                relic.can_spawn = lambda:original_key(relic) not in row['blocked']
                relic.canSpawn = lambda:True
                return relic
            monkeypatch.setattr(module,'make_relic',prepared_relic)
            results = [original_key(pools.draw(row['tier'],from_end=row['from_end'])) for _ in range(3)]
            assert results == row['results']
            assert original_pool_state(pools) == row['after']
        assert calls == row['calls']
        state = parent.export_state()
    assert {key:state[key] for key in row['state']} == row['state']
