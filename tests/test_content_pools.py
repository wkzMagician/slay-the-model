"""Fixed pre-repair references and native-entry content-pool regressions."""
import json
from pathlib import Path
from typing import cast

import pytest

from actions.reward import AddEliteRelicAction, AddRelicAction, AddRandomPotionAction
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from potions.pool import catalog as potion_catalog, definitions as potion_definitions
from relics.pools import RelicPools, catalog as relic_catalog, definitions as relic_definitions
from utils.compatible_random import GameRandom
from utils.random import get_random_potion, get_random_relic
from utils.types import RarityType as R

FIXTURES = Path(__file__).parent/'fixtures'
RELIC_REFERENCE = json.loads((FIXTURES/'relic_pool_reference.json').read_text(encoding='utf-8'))['rows']
POTION_REFERENCE = [json.loads(line) for line in (FIXTURES/'potion_pool_reference.jsonl').read_text(encoding='utf-8').splitlines()]


def required_relic(**kwargs):
    relic = get_random_relic(**kwargs)
    assert relic is not None
    return relic


@pytest.mark.parametrize('row', RELIC_REFERENCE, ids=lambda row:f"{row['role']}-{row['seed']}-{row['tier']}")
def test_all_five_relic_pools_match_preexisting_order_and_shuffle_reference(row):
    game_state.player.namespace = row['role']
    parent = GameRandom(row['seed'])
    seeds = {tier.lower():parent.random_long() for tier in ('COMMON','UNCOMMON','RARE','SHOP','BOSS')}
    pools = RelicPools(seeds)
    assert relic_catalog()['pools'][row['role']][row['tier']] == row['before']
    pools.initialize(row['tier'])
    assert str(seeds[row['tier'].lower()]) == row['shuffle_seed']
    remaining = pools.remaining[row['tier']]
    assert remaining is not None
    assert [relic_definitions()[key]['id'] for key in remaining] == row['after']


@pytest.mark.parametrize('row', POTION_REFERENCE, ids=lambda row:row['role'])
def test_potion_role_pool_matches_actual_preexisting_jar_id_query(row):
    role = {'IRONCLAD':'ironclad','THE_SILENT':'silent','DEFECT':'defect','WATCHER':'watcher'}[row['role']]
    assert potion_catalog()['pools'][role] == row['ordered_ids']


def test_relics_are_reserved_before_obtaining_and_do_not_consume_parent_rng():
    pools = game_state.relic_pools
    pools.remaining['COMMON'] = ['Anchor', 'Vajra', 'BagOfMarbles']
    before = cast(StreamRandom, get_rng('relic')).export_state()
    assert required_relic(rarities=[R.COMMON]).idstr == 'Anchor'
    assert required_relic(rarities=[R.COMMON]).idstr == 'Vajra'
    assert game_state.obtained_relics == set()
    assert pools.remaining['COMMON'] == ['BagOfMarbles']
    assert cast(StreamRandom, get_rng('relic')).export_state() == before


def test_ineligible_relic_is_consumed_then_retry_uses_pool_tail(monkeypatch):
    from relics.global_relics.common import Anchor
    pools = game_state.relic_pools
    pools.remaining['COMMON'] = ['Anchor', 'Vajra', 'BagOfMarbles']
    monkeypatch.setattr(Anchor, 'can_spawn', lambda self:False)
    assert required_relic(rarities=[R.COMMON]).idstr == 'BagOfMarbles'
    assert pools.remaining['COMMON'] == ['Vajra']


def test_tail_draw_falls_back_to_next_tier_head():
    pools = game_state.relic_pools
    pools.remaining.update(SHOP=[], UNCOMMON=['HornCleat','BlueCandle'])
    assert required_relic(rarities=[R.SHOP], from_end=True).idstr == 'HornCleat'
    assert pools.remaining['UNCOMMON'] == ['BlueCandle']


@pytest.mark.parametrize('tier', [R.COMMON,R.UNCOMMON,R.RARE,R.SHOP,R.BOSS])
def test_exhaustion_has_correct_repeatable_fallback_identity(tier):
    game_state.relic_pools.remaining.update({name:[] for name in ('COMMON','UNCOMMON','RARE','SHOP','BOSS')})
    expected = 'RedCirclet' if tier == R.BOSS else 'Circlet'
    assert [required_relic(rarities=[tier]).idstr for _ in range(3)] == [expected]*3


def test_circlet_obtaining_stacks_counter_on_one_object():
    from relics.global_relics.special import Circlet
    game_state.player.relics = []
    for _ in range(3):
        AddRelicAction(Circlet()).execute()
    assert len(game_state.player.relics) == 1
    assert cast(Circlet, game_state.player.relics[0]).counter == 3


def test_owned_relics_are_consumed_and_cannot_reappear():
    from relics.global_relics.common import Anchor
    game_state.player.relics = [Anchor()]
    game_state.relic_pools.remaining['COMMON'] = ['Anchor','Vajra','BagOfMarbles']
    assert required_relic(rarities=[R.COMMON]).idstr == 'BagOfMarbles'
    assert game_state.relic_pools.remaining['COMMON'] == ['Vajra']


@pytest.mark.parametrize('role,starter', [('ironclad','BurningBlood'),('silent','RingOfTheSnake'),('defect','CrackedCore'),('watcher','PureWater')])
def test_starters_and_character_metadata_keep_original_pool_membership(role, starter):
    game_state.player.namespace = role
    pool = game_state.relic_pools
    for tier in ('COMMON','UNCOMMON','RARE','SHOP','BOSS'):
        pool.initialize(tier)
        assert starter not in pool.remaining[tier]
    assert 'OrangePellets' in (pool.remaining['SHOP'] or [])
    assert ('PaperPhrog' in (pool.remaining['UNCOMMON'] or [])) == (role == 'ironclad')
    assert ('SelfFormingClay' in (pool.remaining['UNCOMMON'] or [])) == (role == 'ironclad')
    module = __import__(f'relics.character.{role}', fromlist=[starter])
    assert getattr(module, starter)().rarity == R.STARTER


def test_potion_rejection_retries_the_full_pool(monkeypatch):
    ids = potion_catalog()['pools']['ironclad']
    rare = next(value for value in ids if potion_definitions()[value]['rarity'] == 'RARE')
    common = next(value for value in ids if potion_definitions()[value]['rarity'] == 'COMMON')
    answers = iter([rare,rare,common])
    seen = []
    def choose(values):
        seen.append(list(values))
        return next(answers)
    monkeypatch.setattr(get_rng('potion'), 'choice', choose)
    potion = get_random_potion(['ironclad'], [R.COMMON])
    assert potion is not None
    assert potion._original_potion_id == common
    assert seen == [ids]*3


@pytest.mark.parametrize('roll,rarity', [(0,'COMMON'),(64,'COMMON'),(65,'UNCOMMON'),(89,'UNCOMMON'),(90,'RARE'),(99,'RARE')])
def test_weighted_potion_uses_integer_boundaries_before_full_pool_rejection(roll, rarity, monkeypatch):
    rng = get_rng('potion')
    def integer(start, end):
        assert (start,end) == (0,99)
        return roll
    monkeypatch.setattr(rng, 'random_int', integer)
    monkeypatch.setattr(rng, 'choice', lambda ids:next(value for value in ids if potion_definitions()[value]['rarity'] == rarity))
    potion = get_random_potion(['ironclad'])
    assert potion is not None
    assert potion.rarity == R[rarity]


def test_smoke_bomb_is_only_in_rare_rejection_result(monkeypatch):
    from potions.global_potions import SmokeBomb
    monkeypatch.setattr(get_rng('potion'), 'choice', lambda ids:'SmokeBomb')
    assert isinstance(get_random_potion(['ironclad'], [R.RARE]), SmokeBomb)
    assert SmokeBomb().rarity == R.RARE


@pytest.mark.parametrize('event_name,count', [('lab',3),('woman',1),('woman',2),('woman',3)])
@pytest.mark.parametrize('blocked', ['none','full','sozu'])
@pytest.mark.parametrize('role', ['ironclad','silent','defect','watcher'])
@pytest.mark.parametrize('ascension', [0,20])
def test_native_events_draw_uniform_potions_before_obtain_constraints(event_name, count, blocked, role, ascension, monkeypatch):
    from events.lab import Lab
    from events.woman_in_blue import WomanInBlueEvent
    from potions.global_potions import EnergyPotion
    from relics.global_relics.boss import Sozu
    from player.player_factory import create_player
    game_state.player = create_player(role.capitalize(), ascension=ascension)
    game_state.ascension = ascension
    if event_name == 'lab' and ascension >= 15:
        count = 2
    game_state.player.gold = 100
    if blocked == 'full':
        for _ in range(game_state.player.potion_limit):
            game_state.player.potions.append(EnergyPotion())
    elif blocked == 'sozu':
        game_state.player.relics = [Sozu()]
    game_state.config.auto_select = True
    calls = []
    def choose(ids):
        calls.append(list(ids))
        return ids[0]
    monkeypatch.setattr(get_rng('potion'), 'choice', choose)
    selections = iter([count-1 if event_name == 'woman' else 0] + [0]*5)
    monkeypatch.setattr(game_state, '_resolve_debug_selection', lambda request: [next(selections)])
    event = Lab() if event_name == 'lab' else WomanInBlueEvent()
    event.trigger()
    game_state.drive_actions()
    assert calls == [potion_catalog()['pools'][role]]*count
    if blocked == 'sozu':
        assert not game_state.player.potions


def test_elite_and_chest_obtain_share_exhausted_pool_fallback(monkeypatch):
    from actions.misc import OpenChestAction
    from rooms.treasure import TreasureRoom
    from relics.global_relics.special import Circlet
    game_state.relic_pools.remaining.update(COMMON=[],UNCOMMON=[],RARE=[])
    AddEliteRelicAction().execute()
    room = TreasureRoom()
    room.chest_type = 'small'
    monkeypatch.setattr(get_rng('treasure'), 'random', lambda:0.99)
    OpenChestAction(room).execute()
    game_state.drive_actions()
    circlets = [cast(Circlet, relic) for relic in game_state.player.relics if isinstance(relic, Circlet)]
    assert len(circlets) == 1 and circlets[0].counter == 2
