"""Regressions for distinct consumer retry scopes and permanent transforms."""
from copy import deepcopy
from typing import cast
from unittest.mock import patch

import pytest

from actions.card_choice import ChooseAddRandomCardAction, ChooseObtainCardAction
from actions.card_transform import TransformCardAction, TransformAndUpgradeCardAction
from actions.display import InputRequestAction
from engine.card_generation import fixed_choices, foreign_choices, library_choices, neow_choices, transformed_card
from engine.card_pools import COLORS, CURSE_TRANSFORM_IDS, current_pools, definitions, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from utils.types import PilePosType


def test_discovery_retries_complete_pool_without_rarity_draw(monkeypatch):
    rng = get_rng('card_random')
    seen = []
    indices = iter([0, 0, 1, 1, 2])
    def choose(ids):
        seen.append(list(ids))
        return ids[next(indices)]
    monkeypatch.setattr(rng, 'choice', choose)
    cards = fixed_choices(3, ['ironclad'], None, None, 'combat', rng)
    assert len({original_id(card) for card in cards}) == 3
    assert len(seen) == 5 and all(ids == seen[0] for ids in seen)


@pytest.mark.parametrize('namespace', ['colorless', *COLORS])
@pytest.mark.parametrize('rare_only', [False, True])
def test_neow_keeps_slot_rarity_during_retries(namespace, rare_only):
    rng = get_rng('card') if namespace == 'colorless' else get_rng('neow')
    seen = []
    indices = iter([0, 0, 1, 1, 2])
    def choose(ids):
        seen.append(list(ids))
        return ids[next(indices)]
    with patch.object(StreamRandom, 'random_boolean', return_value=False) as roll, patch.object(rng, 'choice', side_effect=choose):
        cards = neow_choices(3, namespace, rare_only)
    assert roll.call_count == 3
    assert all(call.args == (0.33,) for call in roll.call_args_list)
    assert len(cards) == len({original_id(card) for card in cards}) == 3
    assert len(seen) == 5 and all(ids == seen[0] for ids in seen)
    assert game_state.card_rarity_offset == 5
    if namespace == 'colorless':
        assert seen[0] == sorted(seen[0], key=lambda value: value.encode('utf-16-be'))


def test_foreign_retries_rarity_shuffle_and_pick_together(monkeypatch):
    rarity_rng = cast(StreamRandom, get_rng('card_random'))
    card_rng = get_rng('card')
    events = []
    rolls = iter([54, 54, 55, 85])
    def roll(bound):
        assert bound == 99
        events.append('rarity')
        return next(rolls)
    def shuffle(ids):
        events.append('shuffle')
    def choose(ids):
        events.append('pick')
        assert ids == sorted(ids, key=lambda value: value.encode('utf-16-be'))
        assert all(not definitions()[value].healing for value in ids)
        return ids[0]
    monkeypatch.setattr(rarity_rng, 'random_int', roll)
    monkeypatch.setattr(rarity_rng, 'shuffle', shuffle)
    monkeypatch.setattr(card_rng, 'choice', choose)
    cards = foreign_choices()
    assert [definitions()[original_id(card)].rarity for card in cards] == ['COMMON', 'UNCOMMON', 'RARE']
    assert events == ['rarity', 'shuffle', 'pick'] * 4
    assert game_state.card_rarity_offset == 5


def test_library_retries_rarity_keeps_offset_and_reverses_grid(monkeypatch):
    rng = get_rng('card')
    indices = iter([0, 0, 1, 2])
    calls = []
    def choose(ids):
        calls.append(list(ids))
        return ids[next(indices)]
    monkeypatch.setattr(rng, 'choice', choose)
    with patch.object(StreamRandom, 'random_int', return_value=99) as roll:
        cards = library_choices(3)
    assert roll.call_count == 4
    assert all(ids == calls[0] for ids in calls)
    assert [original_id(card) for card in cards] == ['Warcry', 'Cleave', 'Anger']
    assert game_state.card_rarity_offset == 5


@pytest.mark.parametrize('namespace', COLORS)
@pytest.mark.parametrize('target', ['Anger', 'Strike_R', 'Finesse', 'Injury', 'Unload'])
def test_transform_uses_current_role_and_preserves_all_pools(namespace, target, monkeypatch):
    game_state.player.namespace = namespace
    pools = current_pools()
    before = deepcopy((pools.current, pools.source))
    seen = []
    def choose(ids):
        seen.extend(ids)
        return ids[0]
    rng = get_rng('misc')
    monkeypatch.setattr(rng, 'choice', choose)
    if target == 'Injury':
        monkeypatch.setattr(rng, 'random_int', lambda start, end: 1)
    card = definitions()[target].make_card()
    card.upgrade()
    result = transformed_card(card, rng)
    assert result is not None and original_id(result) != target
    assert target not in seen
    if target == 'Injury':
        assert original_id(result) == [value for value in CURSE_TRANSFORM_IDS if value != target][1]
    elif target == 'Finesse':
        assert seen == [value for value in pools.source[('colorless', None)] if value != target]
    else:
        expected = pools.current[(namespace, 'COMMON')] + pools.source[(namespace, 'UNCOMMON')] + pools.source[(namespace, 'RARE')]
        assert seen == [value for value in expected if value != target]
    assert (pools.current, pools.source) == before


@pytest.mark.parametrize('upgrade', [False, True])
def test_native_transform_actions_replace_exact_object_and_run_obtain_hooks(upgrade):
    from relics.global_relics.common import CeramicFish, Omamori
    original = definitions()['Injury'].make_card()
    player = game_state.player
    player.card_manager.add_to_pile(original, 'deck', PilePosType.TOP)
    ward = Omamori()
    player.relics = [ward, CeramicFish()]
    count = len(player.card_manager.get_pile('deck'))
    action = TransformAndUpgradeCardAction(original, 'deck') if upgrade else TransformCardAction(original, 'deck')
    action.execute()
    game_state.drive_actions()
    assert original not in player.card_manager.get_pile('deck')
    assert len(player.card_manager.get_pile('deck')) == count - 1


@pytest.mark.parametrize('protocol', ['fixed', 'neow', 'foreign'])
@pytest.mark.parametrize('skip', [False, True])
def test_special_choice_menu_take_and_skip(protocol, skip, monkeypatch):
    game_state.config.auto_select = True
    monkeypatch.setattr(game_state, '_resolve_debug_selection', lambda request: [] if skip else [0])
    pile = 'deck' if protocol == 'neow' else 'hand'
    namespace = 'colorless' if protocol == 'neow' else None
    before = len(game_state.player.card_manager.get_pile(pile))
    ChooseAddRandomCardAction(pile=pile, namespace=namespace, selection_kind=protocol).execute()
    menu = cast(InputRequestAction, game_state.action_queue.peek_next())
    assert len(menu.options) == 3
    game_state.drive_actions()
    assert len(game_state.player.card_manager.get_pile(pile)) == before + (not skip)


def test_library_native_menu_has_twenty_cards_without_bowl():
    from relics.global_relics.uncommon import SingingBowl
    game_state.player.relics = [SingingBowl()]
    ChooseObtainCardAction(total=20, selection_kind='library', can_skip=False).execute()
    menu = cast(InputRequestAction, game_state.action_queue.peek_next())
    assert len(menu.options) == 20 and menu.must_select
    assert game_state.card_rarity_offset == 5


def test_transform_draw_failure_keeps_original_deck_and_pool_state(monkeypatch):
    from actions.card_lifecycle import AddCardAction
    original = definitions()['Finesse'].make_card()
    AddCardAction(original, dest_pile='deck').execute()
    before = deepcopy((current_pools().current, current_pools().source))
    def fail(ids):
        raise RuntimeError('prepared RNG failure')
    monkeypatch.setattr(get_rng('misc'), 'choice', fail)
    with pytest.raises(RuntimeError, match='prepared RNG failure'):
        TransformCardAction(original, 'deck').execute()
    assert original in game_state.player.card_manager.get_pile('deck')
    assert (current_pools().current, current_pools().source) == before
    assert game_state.action_queue.is_empty()


@pytest.mark.parametrize('upgrade', [False, True])
def test_transform_obtain_runs_egg_and_ceramic_fish_once(upgrade, monkeypatch):
    from actions.card_lifecycle import AddCardAction
    from relics.global_relics.common import CeramicFish
    from relics.global_relics.uncommon import MoltenEgg
    original = definitions()['Anger'].make_card()
    AddCardAction(original, dest_pile='deck').execute()
    player = game_state.player
    player.relics = [MoltenEgg(), CeramicFish()]
    before_gold = player.gold
    before_count = len(player.card_manager.get_pile('deck'))
    monkeypatch.setattr(get_rng('misc'), 'choice', lambda ids: 'Cleave')
    action = TransformAndUpgradeCardAction(original, 'deck') if upgrade else TransformCardAction(original, 'deck')
    action.execute()
    game_state.drive_actions()
    assert original not in player.card_manager.get_pile('deck')
    assert len(player.card_manager.get_pile('deck')) == before_count
    assert player.gold == before_gold + 9
    obtained = next(card for card in player.card_manager.get_pile('deck') if original_id(card) == 'Cleave')
    assert obtained.upgrade_level == 1


def test_library_previews_each_accepted_card_before_the_next_roll(monkeypatch):
    from types import SimpleNamespace
    events = []
    def preview(card, pile):
        events.append('preview')
        return False
    def roll(bound):
        events.append('rarity')
        return 99
    game_state.player.relics = [SimpleNamespace(should_upgrade_added_card=preview)]
    rng = get_rng('card')
    monkeypatch.setattr(rng, 'random_int', roll)
    indices = iter([0, 1, 2])
    monkeypatch.setattr(rng, 'choice', lambda ids: ids[next(indices)])
    library_choices(3)
    assert events == ['rarity', 'preview'] * 3


@pytest.mark.parametrize('kind', ['discovery', 'foreign'])
@pytest.mark.parametrize('upgraded', [False, True])
def test_real_card_play_reaches_special_menu_and_obtains_selected_card(kind, upgraded, monkeypatch):
    from actions.combat_cards import PlayCardAction
    from cards.colorless.discovery import Discovery
    from cards.watcher.foreign_influence import ForeignInfluence
    from enemies.act1.cultist import Cultist
    from tests.test_combat_utils import create_test_helper
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    helper.start_combat([Cultist()])
    helper.game_state.drive_actions()
    card = Discovery() if kind == 'discovery' else ForeignInfluence()
    if upgraded:
        card.upgrade()
    requests = []
    def select(request):
        requests.append(request)
        return [0]
    monkeypatch.setattr(game_state, '_resolve_debug_selection', select)
    before = list(player.card_manager.get_pile('hand'))
    helper.add_card_to_hand(card)
    game_state.add_action(PlayCardAction(card))
    game_state.drive_actions()
    assert len(requests) == 1 and len(requests[0].options) == 3
    selected = requests[0].options[0].actions[0].card
    assert selected in player.card_manager.get_pile('hand')
    assert selected not in before and card not in player.card_manager.get_pile('hand')


def test_native_neow_event_binds_all_four_choice_blessings_to_neow_protocol():
    from events.neo_event import NeoEvent
    calls = []
    # _show_four_blessings creates a fresh stream; observe the class adapter.
    original = StreamRandom.choice
    def observe(self, values):
        calls.append(values)
        return original(self, values)
    with patch.object(StreamRandom, 'choice', observe):
        NeoEvent()._show_four_blessings()
    card_choices = [action for options in calls for option in options for action in option.actions
                    if isinstance(action, ChooseAddRandomCardAction)]
    assert len(card_choices) == 4
    assert all(cast(ChooseAddRandomCardAction, action).selection_kind == 'neow' for action in card_choices)


def test_extension_namespace_retains_registration_provider_contract(monkeypatch):
    from types import SimpleNamespace
    from utils.types import RarityType
    selected = []
    first = SimpleNamespace(idstr='extension.First')
    def draw(**kwargs):
        selected.append(list(kwargs['exclude_card_ids']))
        assert kwargs['namespaces'] == ['extension']
        assert kwargs['rarities'] == [RarityType.COMMON]
        return first if not kwargs['exclude_card_ids'] else None
    monkeypatch.setattr('utils.random.get_random_card', draw)
    cards = fixed_choices(3, ['extension'], [RarityType.COMMON], None, 'combat', get_rng('card_random'))
    assert cards == [first]
    assert selected == [[], ['extension.First'], ['extension.First']]
