"""Reconstructed Merchant acceptance loop with actual original JAR selectors."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from engine.card_pools import original_id
from engine.game_state import game_state
from engine.random_streams import get_rng, StreamRandom
from rooms.shop_state import generate_colored_cards, generate_colorless_cards
from tests.test_special_card_reference import trace_rng

ROWS = json.loads(gzip.decompress((Path(__file__).parent/'fixtures/shop_card_reference.json.gz').read_bytes()))
COLORS = {'RED':'ironclad','GREEN':'silent','BLUE':'defect','PURPLE':'watcher'}


@pytest.mark.parametrize('row',ROWS)
def test_merchant_candidates_calls_and_state(row,monkeypatch):
    game_state.player.namespace = COLORS[row['color']]
    game_state.player.relics = []
    game_state.ascension = row['ascension']
    game_state.card_rarity_offset = row['offset']
    from rooms.shop import ShopRoom
    game_state.current_room = ShopRoom()
    rng = cast(StreamRandom,get_rng('card'))
    rng.seed(int(row['seed']))
    calls = trace_rng(rng,monkeypatch)
    cards = generate_colored_cards(game_state.player)+generate_colorless_cards()
    assert not row['power_fallback']
    assert [original_id(card) for card in cards] == row['cards']
    assert calls == row['calls']
    state = rng.export_state()
    assert {key:state[key] for key in row['state']} == row['state']
    assert game_state.card_rarity_offset == row['after_offset']
