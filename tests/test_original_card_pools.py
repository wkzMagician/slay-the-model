"""Fixed-source/JDK reference, archived on 2026-10-29 before this repair."""
import json
from pathlib import Path
import pytest

from engine.card_pools import CardPools, definitions, java_id_key, original_id
from engine.game_state import game_state
from engine.random_streams import get_rng
from utils.random import get_random_card
from utils.types import RarityType as R, CardType as T

REFERENCE = json.loads((Path(__file__).parent/'fixtures/card_pool_reference.json').read_text(encoding='utf-8'))['pools']
COLORS = {'RED':'ironclad', 'GREEN':'silent', 'BLUE':'defect', 'PURPLE':'watcher', 'COLORLESS':'colorless', 'CURSE':'curse'}


@pytest.mark.parametrize('row', REFERENCE, ids=lambda row:row['color']+row.get('rarity',''))
def test_current_and_source_match_preexisting_reference(row):
    pools = CardPools()
    key = (COLORS[row['color']], row.get('rarity'))
    assert pools.current[key] == row['initialized']
    assert pools.source[key] == row['source_copy']
    pools.current[key].clear()
    assert pools.source[key] == row['source_copy']
    assert CardPools().current[key] == row['initialized']


@pytest.mark.parametrize('color', list(COLORS.values())[:4])
@pytest.mark.parametrize('rarity', [R.COMMON,R.UNCOMMON,R.RARE])
@pytest.mark.parametrize('kind', [T.ATTACK,T.SKILL,T.POWER])
def test_shop_sorts_original_id_after_filters(color, rarity, kind):
    pools = CardPools()
    rows = definitions()
    expected = sorted([value for value in pools.current[(color,rarity.name)] if rows[value].type == kind.name], key=java_id_key)
    assert pools.candidates([color],[rarity],[kind],pool_kind='shop') == expected


def test_original_metadata_keeps_existing_card_definition_separate():
    from engine.card_pools import original_rarity
    card = definitions()['Unload'].make_card()
    assert original_rarity(card) == R.RARE
    # CARD-064 is an independently recorded definition defect.
    assert card.rarity == R.UNCOMMON
    assert original_id(card.copy()) == 'Unload'


def test_combat_source_order_and_current_mutations_are_independent():
    pools = CardPools()
    game_state.card_pools = pools
    expected = sum([pools.source[('ironclad',tier)] for tier in ('COMMON','UNCOMMON','RARE')], [])
    expected = [value for value in expected if not definitions()[value].healing]
    assert pools.candidates(['ironclad'],pool_kind='combat') == expected
    pools.current[('ironclad','COMMON')].clear()
    assert pools.candidates(['ironclad'],pool_kind='combat') == expected


def test_same_index_selects_original_pool_identity(monkeypatch):
    monkeypatch.setattr(get_rng('card_random'),'choice',lambda seq:seq[1])
    card = get_random_card(['ironclad'],[R.COMMON],pool_kind='current')
    assert original_id(card) == 'Cleave'
