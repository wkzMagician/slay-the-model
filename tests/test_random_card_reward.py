"""Reward protocol controls use real state/cards and observe integer RNG calls."""
from collections import Counter
from types import SimpleNamespace
from unittest.mock import patch
from typing import cast

import pytest

from engine.card_pools import CardPools, original_id, original_rarity
from engine.card_rewards import reward_cards, roll_rarity, update_compensation
from engine.game_state import game_state
from engine.random_streams import get_rng, StreamRandom
from utils.random import CARD_RARITY_PROBABILITIES, get_random_card, get_random_card_reward
from utils.types import RarityType as R


@pytest.mark.parametrize('kind,expected', [('normal',(60,37,3)), ('elite',(50,40,10)), ('shop',(54,37,9))])
def test_base_rates(kind, expected):
    assert tuple(CARD_RARITY_PROBABILITIES[kind][r] for r in (R.COMMON,R.UNCOMMON,R.RARE)) == expected


@pytest.mark.parametrize('kind,expected', [('normal',(65,35,0)), ('elite',(55,40,5)), ('shop',(59,37,4))])
def test_initial_integer_boundaries(kind, expected):
    assert game_state.card_rarity_offset == 5
    with patch.object(StreamRandom, 'random_int', side_effect=range(100)) as draw:
        counts = Counter(roll_rarity(get_rng('card'), kind) for _ in range(100))
    assert tuple(counts[r] for r in (R.COMMON,R.UNCOMMON,R.RARE)) == expected
    assert all(call.args == (99,) for call in draw.call_args_list)
    assert game_state.card_rarity_offset == 5


def test_compensation_floor_reset_and_compatibility_property():
    for _ in range(100):
        update_compensation(R.COMMON)
    assert game_state.card_rarity_offset == -40
    assert game_state.card_chance_common_counter == 45
    update_compensation(R.UNCOMMON)
    assert game_state.card_rarity_offset == -40
    update_compensation(R.RARE)
    assert game_state.card_chance_common_counter == 0
    game_state.card_chance_common_counter = 20
    assert game_state.card_rarity_offset == -15


def test_nloth_changes_rare_threshold_before_uncommon_boundary():
    game_state.player.relics = [SimpleNamespace(idstr='NlothGift')]
    game_state.card_rarity_offset = 0
    with patch.object(StreamRandom, 'random_int', side_effect=range(100)):
        counts = Counter(roll_rarity(get_rng('card')) for _ in range(100))
    assert counts == {R.RARE:9, R.UNCOMMON:37, R.COMMON:54}


def test_duplicate_retries_use_full_same_tier_and_update_only_once():
    observations = []
    indices = iter([0,0,1,1,2])
    def pick(seq):
        observations.append(list(seq))
        return seq[next(indices)]
    with patch.object(StreamRandom, 'random_int', return_value=99) as roll, patch.object(StreamRandom, 'choice', side_effect=pick):
        cards = reward_cards(3, ['ironclad'], allow_upgraded=False)
    assert [original_id(c) for c in cards] == ['Anger','Cleave','Warcry']
    assert len(observations) == 5 and all(pool == observations[0] for pool in observations)
    assert len(observations[0]) == 20
    assert roll.call_count == 3
    assert game_state.card_rarity_offset == 2


@pytest.mark.parametrize('act,asc,chance', [(1,0,0),(2,0,.25),(3,0,.5),(2,12,.125),(3,20,.25)])
def test_all_candidates_precede_upgrade_calls(act, asc, chance):
    game_state.current_act, game_state.ascension = act, asc
    events = []
    indices = iter([0,1,2])
    def pick(seq):
        events.append('card')
        return seq[next(indices)]
    def boolean(value):
        events.append(('upgrade',value))
        return False
    with patch.object(StreamRandom,'random_int',return_value=99), patch.object(StreamRandom,'choice',side_effect=pick), patch.object(StreamRandom,'random_boolean',side_effect=boolean):
        cards = reward_cards(3,['ironclad'])
    assert events == ['card']*3 + [('upgrade',chance)]*3
    assert all(c.upgrade_level == 0 for c in cards)


def test_rare_skips_random_upgrade_but_egg_previews_still_apply():
    from relics.global_relics.uncommon import MoltenEgg
    game_state.player.relics = [MoltenEgg()]
    game_state.card_rarity_offset = -40
    game_state.current_act = 3
    def choose_attack(seq):
        from engine.card_pools import definitions
        return next(value for value in seq if definitions()[value].type == 'ATTACK')
    with patch.object(StreamRandom,'random_int',return_value=0), patch.object(StreamRandom,'choice',side_effect=choose_attack), patch.object(StreamRandom,'random_boolean') as boolean:
        cards = reward_cards(1,['ironclad'],preview_pile='deck')
    assert original_rarity(cards[0]) == R.RARE
    assert cards[0].upgrade_level == 1
    boolean.assert_not_called()


def test_generation_changes_compensation_and_claim_does_not():
    from actions.card_choice import ChooseObtainCardAction
    from actions.card_lifecycle import AddCardAction
    from actions.display import InputRequestAction
    with patch.object(StreamRandom,'random_int',return_value=99), patch.object(StreamRandom,'choice',side_effect=lambda seq:seq[-1]):
        ChooseObtainCardAction(total=1,namespace='ironclad',use_rolling_offset=True).execute()
    assert game_state.card_rarity_offset == 4
    menu = game_state.action_queue.peek_next()
    assert isinstance(menu, InputRequestAction)
    card = cast(AddCardAction, cast(InputRequestAction, menu).options[0].actions[0]).card
    AddCardAction(card=card,dest_pile='deck',source='reward').execute()
    assert game_state.card_rarity_offset == 4


def test_insufficient_pool_terminates_without_tier_fallback():
    pools = CardPools()
    pools.current[('ironclad','COMMON')] = ['Anger']
    game_state.card_pools = pools
    with patch.object(StreamRandom,'random_int',side_effect=lambda bound: 99 if bound == 99 else 0):
        result = reward_cards(3,['ironclad'],allow_upgraded=False)
    assert [original_id(c) for c in result] == ['Anger']
    assert game_state.card_rarity_offset == 2


@pytest.mark.parametrize('method', ['reward','generic'])
def test_exclusions_accept_project_identity(method):
    first = get_random_card_reward(['ironclad'])
    assert first is not None
    for _ in range(50):
        card = (get_random_card_reward(['ironclad'],exclude_set=[first.idstr]) if method == 'reward'
                else get_random_card(['ironclad'],exclude_card_ids=[first.idstr]))
        assert card is None or card.idstr != first.idstr


@pytest.mark.parametrize('selection', ['take','skip','bowl'])
def test_real_reward_menu_resolution_preserves_generation_compensation(selection, monkeypatch):
    from actions.card_choice import ChooseObtainCardAction
    from relics.global_relics.uncommon import SingingBowl
    game_state.config.auto_select = True
    if selection == 'bowl':
        game_state.player.relics = [SingingBowl()]
    deck_before = len(game_state.player.card_manager.get_pile('deck'))
    hp_before = game_state.player.max_hp
    def select(request):
        return [] if selection == 'skip' else [len(request.options)-1] if selection == 'bowl' else [0]
    monkeypatch.setattr(game_state,'_resolve_debug_selection',select)
    action = ChooseObtainCardAction(total=3,namespace='ironclad',use_rolling_offset=True,allow_upgraded=True)
    action.execute()
    offset = game_state.card_rarity_offset
    state = cast(StreamRandom, get_rng('card')).export_state()
    game_state.drive_actions()
    assert game_state.card_rarity_offset == offset
    assert cast(StreamRandom, get_rng('card')).export_state() == state
    assert len(game_state.player.card_manager.get_pile('deck')) == deck_before + (selection == 'take')
    assert game_state.player.max_hp == hp_before + (2 if selection == 'bowl' else 0)


def test_any_color_helper_consumes_a_shuffle_long_before_each_pick(monkeypatch):
    rng = cast(StreamRandom, get_rng('card'))
    long_draw = rng.random_long
    observed = []
    def observe():
        observed.append('long')
        return long_draw()
    monkeypatch.setattr(rng,'random_long',observe)
    cards = reward_cards(3,None,allow_upgraded=False)
    assert len(cards) == len({original_id(c) for c in cards}) == 3
    assert len(observed) >= 3
    assert all(card.namespace in ('ironclad','silent','defect','watcher','colorless') for card in cards)
