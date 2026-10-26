"""Normal startup must populate rewards without test-side card imports."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
FRESH_START = r'''
import collections,contextlib,io,json,random,sys
with contextlib.redirect_stdout(io.StringIO()):
    import potions,powers.definitions,relics
    from player.player_factory import create_player
    from engine.game_state import game_state
    from utils.registry import get_registered,list_registered
    from utils.random import get_random_card
    from utils.types import RarityType
    character=sys.argv[1]
    random.seed(int(sys.argv[2]))
    player=create_player(character)
    game_state.player=player
    game_state.config.mode='debug'
    game_state.config.auto_select=True
    game_state.config.debug['select_type']='first'
    cards={}
    for key in list_registered('card'):
        card=get_registered('card',key)()
        if card.namespace==player.namespace:
            cards[key]=card.rarity.name
    pools={}
    real_choice=random.choice
    seen=[]
    def observe_choice(seq):
        if seq and isinstance(seq[0],str):seen.append(list(seq))
        return real_choice(seq)
    random.choice=observe_choice
    try:
        for rarity in [RarityType.COMMON,RarityType.UNCOMMON,RarityType.RARE]:
            result=get_random_card(namespaces=[player.namespace],rarities=[rarity])
            assert result is not None
            assert result.namespace==player.namespace and result.rarity==rarity
            pools[rarity.name]=seen[-1]
    finally:
        random.choice=real_choice
    starting=[card.idstr for card in player.card_manager.piles['deck']]
    # Run the real card reward choice and permanent acquisition paths.
    from actions.card import ChooseObtainCardAction
    for _ in range(12):
        game_state.add_action(ChooseObtainCardAction(total=3,namespace=player.namespace))
        game_state.drive_actions()
    obtained=[card.idstr for card in player.card_manager.piles['deck'][len(starting):]]
print(json.dumps(dict(namespace=player.namespace,cards=cards,pools=pools,
    starting=starting,obtained=obtained)))
'''


def fresh_start(character: str, seed: int = 1024) -> dict:
    result = subprocess.run(
        [sys.executable, '-c', FRESH_START, character, str(seed)],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.fixture(scope='module')
def ironclad_pool():
    return fresh_start('Ironclad')


def test_normal_startup_registers_all_ironclad_cards(ironclad_pool):
    assert len(ironclad_pool['cards']) == 75
    assert {k for k,v in ironclad_pool['cards'].items() if v == 'STARTER'} == {'Strike','Defend','Bash'}
    assert {'ShrugItOff','Feed','Corruption','Barricade','Whirlwind'} <= ironclad_pool['cards'].keys()


@pytest.mark.parametrize('rarity,count', [('COMMON',20),('UNCOMMON',36),('RARE',16)])
def test_real_reward_filter_includes_full_rarity_pool(ironclad_pool,rarity,count):
    pool = ironclad_pool['pools'][rarity]
    assert len(pool) == len(set(pool)) == count
    assert all(ironclad_pool['cards'][name] == rarity for name in pool)
    assert not {'Strike','Defend','Bash'} & set(pool)


def test_starting_deck_is_unchanged(ironclad_pool):
    assert ironclad_pool['starting'] == ['ironclad.Strike']*5 + ['ironclad.Defend']*4 + ['ironclad.Bash']


@pytest.mark.parametrize('seed', [1,42,1024])
def test_normal_reward_choice_actually_grants_previously_missing_cards(seed):
    pool = fresh_start('Ironclad', seed)
    formerly_available = {
        'Anger','IronWave','PommelStrike','HeavyBlade','Armaments','Flex',
        'Clothesline','Inflame','BodySlam','Carnage','Bludgeon','LimitBreak',
        'Pummel','Uppercut','Offering',
    }
    assert len(pool['obtained']) == 12
    assert all(card.startswith('ironclad.') for card in pool['obtained'])
    assert any(card.split('.')[-1] not in formerly_available for card in pool['obtained'])
    assert not {'ironclad.Strike','ironclad.Defend','ironclad.Bash'} & set(pool['obtained'])


@pytest.mark.parametrize('character,namespace', [('Silent','silent'),('Defect','defect'),('Watcher','watcher')])
def test_other_character_normal_startups_keep_their_own_rewards(character,namespace):
    pool = fresh_start(character)
    assert pool['namespace'] == namespace
    assert all(card.startswith(namespace+'.') for card in pool['starting'])
    assert all(card.startswith(namespace+'.') for card in pool['obtained'])
    assert sum(len(v) for v in pool['pools'].values()) == 71
