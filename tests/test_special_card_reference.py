"""Fixed-JAR special helpers and source-reconstructed Library loop reference."""
import json
from pathlib import Path
from typing import cast

import pytest

from engine.card_generation import fixed_choices, foreign_choices, library_choices, neow_choices, transformed_card
from engine.card_pools import current_pools, definitions, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng

FIXTURES = Path(__file__).parent/'fixtures'
REFERENCE = json.loads((FIXTURES/'special_card_reference.json').read_text(encoding='utf-8'))
COLORS = {'RED':'ironclad', 'GREEN':'silent', 'BLUE':'defect', 'PURPLE':'watcher'}


def trace_rng(rng, monkeypatch):
    calls = []
    integer, boolean, long = rng.random_int, rng.random_boolean, rng.random_long
    def draw(start, end=None):
        value = integer(start, end)
        calls.append(['int', start, value] if end is None else ['int_range', start, end, value])
        return value
    def flip(chance):
        value = boolean(chance)
        # JAR parameters are float32, so retain the same exact input value.
        from utils.compatible_random import float32
        calls.append(['boolean', float32(chance), value])
        return value
    def draw_long():
        value = long()
        calls.append(['long', str(value)])
        return value
    monkeypatch.setattr(rng, 'random_int', draw)
    monkeypatch.setattr(rng, 'random_boolean', flip)
    monkeypatch.setattr(rng, 'random_long', draw_long)
    return calls


@pytest.mark.parametrize('row', REFERENCE, ids=lambda row:row['color']+'-'+row['seed']+'-'+row['protocol'])
def test_special_selection_ids_calls_and_four_final_stream_states(row, monkeypatch):
    namespace = COLORS[row['color']]
    game_state.player.namespace = namespace
    game_state.card_rarity_offset = row['offset']
    pools = current_pools()
    if row['mutated_current']:
        pools.current[(namespace, 'COMMON')].pop(0)
    seed = int(row['seed'])
    rngs = {}
    calls = {}
    for name, delta in [('card', 1), ('card_random', 2), ('neow', 0), ('misc', 3)]:
        rng = cast(StreamRandom, get_rng(name))
        rng.seed(seed + delta)
        rngs[name] = rng
        calls[name] = trace_rng(rng, monkeypatch)
    protocol = row['protocol']
    if protocol == 'discovery':
        cards = fixed_choices(3, [namespace], None, None, 'combat', rngs['card_random'])
    elif protocol == 'colorless_discovery':
        cards = fixed_choices(3, ['colorless'], None, None, 'combat', rngs['card_random'])
    elif protocol == 'foreign':
        cards = foreign_choices()
    elif protocol.startswith('neow_'):
        cards = neow_choices(3, 'colorless' if protocol.endswith('colorless') else namespace, 'rare' in protocol)
    elif protocol == 'library':
        cards = library_choices()
    else:
        card = transformed_card(definitions()[protocol.removeprefix('transform_')].make_card(), rngs['misc'])
        assert card is not None
        cards = [card]
    assert [original_id(card) for card in cards] == row['cards']
    assert calls == row['calls']
    for name, expected in row['states'].items():
        actual = rngs[name].export_state()
        assert {key:actual[key] for key in expected} == expected
    assert game_state.card_rarity_offset == row['offset']


def test_pool_metadata_matches_independent_fixed_source_catalog():
    catalog = json.loads((FIXTURES/'special_card_catalog.json').read_text(encoding='utf-8'))
    rows = definitions()
    for expected in catalog:
        actual = rows[expected['id']]
        assert (actual.rarity, actual.type, actual.healing) == (expected['rarity'], expected['type'], expected['healing'])
