"""Actual fixed-JAR getRewardCards, with prepared metadata cards (see fixture notes)."""
import json
from pathlib import Path
import pytest
from typing import cast

from engine.card_pools import original_id
from engine.card_rewards import reward_cards
from engine.game_state import game_state
from engine.random_streams import get_rng, StreamRandom

ROWS = json.loads((Path(__file__).parent/'fixtures/original_reward_reference.json').read_text(encoding='utf-8'))
COLORS = {'RED':'ironclad','GREEN':'silent','BLUE':'defect','PURPLE':'watcher'}


@pytest.mark.parametrize('row', ROWS, ids=lambda r:'-'.join(str(r[k]) for k in ('color','seed','offset','act','ascension','encounter')))
def test_original_jar_reward_candidates_calls_offset_and_state(row, monkeypatch):
    game_state.card_rarity_offset = row['offset']
    game_state.current_act, game_state.ascension = row['act'], row['ascension']
    rng = cast(StreamRandom, get_rng('card'))
    rng.seed(int(row['seed']))
    calls = []
    real_int, real_boolean = rng.random_int, rng.random_boolean
    def draw(bound):
        value = real_int(bound)
        calls.append(['int',bound,value])
        return value
    def boolean(chance):
        value = real_boolean(chance)
        calls.append(['boolean',chance,value])
        return value
    monkeypatch.setattr(rng,'random_int',draw)
    monkeypatch.setattr(rng,'random_boolean',boolean)
    result = reward_cards(3,[COLORS[row['color']]],row['encounter'])
    assert [[original_id(card),card.upgrade_level] for card in result] == row['cards']
    assert calls == row['calls']
    assert game_state.card_rarity_offset == row['after_offset']
    state = rng.export_state()
    assert {key:state[key] for key in row['state']} == row['state']
