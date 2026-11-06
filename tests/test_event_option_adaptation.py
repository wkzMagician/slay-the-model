"""Event option availability, displayed costs, and actual effects."""
from engine.random_streams import get_rng, StreamRandom
import importlib
import inspect
from typing import cast
from types import SimpleNamespace
from pathlib import Path

import pytest

from actions.combat import HealAction, LoseHPAction
from actions.display import InputRequestAction, build_selected_options, show_selected_options
from actions.reward import AddGoldAction, AddRandomPotionAction, LoseGoldAction
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from events.base_event import Event
from events.big_fish import BigFishEvent
from events.knowing_skull import KnowingSkull
from events.mind_bloom import MindBloom
from events.scrap_ooze import ScrapOoze
from events.the_cleric import TheClericEvent
from events.wing_statue import WingStatue
from events.woman_in_blue import WomanInBlueEvent
from localization import LocalStr, resolve_text, set_language, t
from tests.test_combat_utils import create_test_helper
from utils.option import Option, option_label


@pytest.fixture
def player():
    helper = create_test_helper()
    result = helper.create_player(hp=20, max_hp=81)
    result.gold = 100
    game_state.action_queue.clear()
    return result


def menu_for(event: Event) -> InputRequestAction:
    game_state.action_queue.clear()
    event.trigger()
    menu = game_state.action_queue.queue[-1]
    assert isinstance(menu, InputRequestAction)
    return menu


@pytest.mark.parametrize('ascension,cost', [(14, 50), (15, 75)])
@pytest.mark.parametrize('gold', [0, 34, 35, 49, 50, 74, 75])
def test_cleric_preserves_indices_locks_cost_boundaries_and_heals(player, ascension, cost, gold):
    game_state.ascension = ascension
    player.gold = gold
    options = menu_for(TheClericEvent()).options
    assert len(options) == 3
    assert [o.enabled for o in options] == [gold >= 35, gold >= cost, True]
    assert str(cost) in resolve_text(options[1].detail)
    assert '20' in resolve_text(options[0].detail)
    for index in (0, 1):
        if not options[index].enabled:
            assert build_selected_options(options, [index]) == {}
            assert str((35, cost)[index]) in option_label(options[index])
    if gold >= 35:
        options[0].actions[0].execute()
        options[0].actions[1].execute()
        assert player.gold == gold - 35
        assert player.hp == 40


@pytest.mark.parametrize('damage,enabled', [(9, False), (10, True)])
def test_wing_statue_keeps_destroy_at_same_index(player, monkeypatch, damage, enabled):
    attack = Strike(base_damage=damage)
    player.card_manager.piles['deck'] = [attack]
    monkeypatch.setattr(get_rng("misc"), "randint", lambda *_: 67)
    options = menu_for(WingStatue()).options
    assert len(options) == 3
    assert options[1].enabled is enabled
    assert '67' in resolve_text(options[1].detail)
    assert '10' in resolve_text(options[1].disabled_reason)
    assert isinstance(options[1].actions[0], AddGoldAction)
    assert options[1].actions[0].amount == 67
    if not enabled:
        assert build_selected_options(options, [1]) == {}


@pytest.mark.parametrize('gold,available', [(49, False), (50, True)])
def test_woman_in_blue_entry_threshold_is_used_by_event_pool(player, gold, available):
    from events.event_pool import EventPool
    event_pool = EventPool()
    event_pool.register_event(WomanInBlueEvent, "woman_in_blue")
    player.gold = gold
    assert WomanInBlueEvent.can_appear() is available
    assert any(m.event_class is WomanInBlueEvent for m in event_pool.get_available_events(1)) is available


@pytest.mark.parametrize('ascension,hp_loss', [(14, 0), (15, 5)])
def test_woman_in_blue_always_offers_three_purchases_and_correct_leave_damage(player, ascension, hp_loss):
    game_state.ascension = ascension
    player.gold = 0  # Direct construction still retains unlocked purchase options.
    options = menu_for(WomanInBlueEvent()).options
    assert len(options) == 4
    assert all(o.enabled for o in options)
    for option, count, cost in zip(options[:3], (1, 2, 3), (20, 30, 40)):
        assert str(cost) in resolve_text(option.detail)
        assert sum(isinstance(a, AddRandomPotionAction) for a in option.actions) == count
        assert isinstance(option.actions[0], LoseGoldAction)
        assert option.actions[0].amount == cost
    loss_actions = [a for a in options[3].actions if isinstance(a, LoseHPAction)]
    assert len(loss_actions) == int(hp_loss > 0)
    if loss_actions:
        assert loss_actions[0].amount == hp_loss
        assert str(hp_loss) in resolve_text(options[3].detail)
        loss_actions[0].execute()
    assert player.hp == 20 - hp_loss


@pytest.mark.parametrize('floor,rich', [(35, True), (40, True), (41, False), (49, False), (50, True), (90, True), (91, False)])
def test_mind_bloom_generates_only_applicable_third_option(player, floor, rich):
    game_state.current_floor = floor
    options = menu_for(MindBloom()).options
    assert len(options) == 3
    assert all(option.enabled for option in options)
    assert resolve_text(options[2].name) == t('events.mind_bloom.' + ('i_am_rich' if rich else 'i_am_healthy'))
    if rich:
        assert isinstance(options[2].actions[0], AddGoldAction)
        assert options[2].actions[0].amount == 999
    else:
        assert isinstance(options[2].actions[0], HealAction)
        assert options[2].actions[0].percent == 1.0


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_big_fish_uses_actual_heal_and_exposes_curse(player, language):
    set_language(language)
    options = menu_for(BigFishEvent()).options
    assert '27' in resolve_text(options[0].detail)
    assert isinstance(options[0].actions[0], HealAction)
    options[0].actions[0].execute()
    assert player.hp == 47
    assert ('Regret' if language == 'en' else '悔恨') in resolve_text(options[2].detail)
    assert all('Option' not in resolve_text(o.name) for o in options)


@pytest.mark.parametrize('ascension,base', [(0, 3), (15, 5)])
def test_scrap_ooze_refreshes_hp_and_probability_after_failed_attempt(player, monkeypatch, ascension, base):
    game_state.ascension = ascension
    event = ScrapOoze()
    option = menu_for(event).options[0]
    assert str(base) in resolve_text(option.detail) and '25%' in resolve_text(option.detail)
    assert isinstance(option.actions[0], LoseHPAction)
    option.actions[0].execute()
    monkeypatch.setattr(get_rng("misc"), "random", lambda: 1.0)
    event._resolve_reach()
    refreshed = cast(InputRequestAction, game_state.action_queue.queue[-1])
    assert isinstance(refreshed, InputRequestAction)
    assert str(base + 1) in resolve_text(refreshed.options[0].detail)
    assert '35%' in resolve_text(refreshed.options[0].detail)
    assert player.hp == 20 - base


@pytest.mark.parametrize('ascension', [0, 15])
def test_skull_refreshes_only_the_chosen_reward_cost(player, ascension):
    player.max_hp = 100
    game_state.ascension = ascension
    event = KnowingSkull()
    for costs in ((6, 6, 6), (7, 6, 6)):
        options = menu_for(event).options
        for option, expected in zip(options[:3], costs):
            assert str(expected) in resolve_text(option.detail)
            assert isinstance(option.actions[0], LoseHPAction)
            assert option.actions[0].amount == expected
        event._increment_cost('potion')


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_nloth_resolves_relic_name_and_trade_effect(player, language):
    from events.nloth import Nloth
    from relics.global_relics.event import GoldenIdol, NlothGift
    set_language(language)
    player.relics = [GoldenIdol(), NlothGift()]
    options = menu_for(Nloth()).options
    for option in options[:2]:
        assert isinstance(option.name, LocalStr)
        assert option.name.kwargs['relic'].resolve() in resolve_text(option.name)
        assert 'events.' not in resolve_text(option.detail)
        assert '{' not in resolve_text(option.detail)
        assert ('恩洛斯的礼物' if language == 'zh' else "N'loth's Gift") in resolve_text(option.detail)


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_matching_card_states_are_localized_and_keep_locked_indices(player, monkeypatch, language):
    module = importlib.import_module('events.match_and_keep')
    set_language(language)
    card = Strike()
    monkeypatch.setattr(module, '_matching_state', {
        'deck': [{'card': card, 'matched': True, 'revealed': True},
                 {'card': card, 'matched': False, 'revealed': True},
                 {'card': card, 'matched': False, 'revealed': False}],
        'tries_remaining': 4,
    })
    module.MatchAndKeepAction().execute()
    menu = cast(InputRequestAction, game_state.action_queue.queue[0])
    assert isinstance(menu, InputRequestAction)
    assert [o.enabled for o in menu.options] == [False, False, True]
    assert resolve_text(menu.options[0].name) == t('events.match_and_keep.matched', card=card.info())
    assert resolve_text(menu.options[1].name) == t('events.match_and_keep.face_up', card=card.info())
    assert resolve_text(menu.options[2].name) == t('events.match_and_keep.face_down', number=3)
    assert list(build_selected_options(menu.options, [2])) == [2]


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_selected_option_echo_includes_effect_text(monkeypatch, language):
    set_language(language)
    lines = []
    monkeypatch.setattr('actions.display.emit_lines', lines.extend)
    monkeypatch.setattr('actions.display.flush_runtime_events', lambda: None)
    detail = LocalStr('events.gain_gold', gold=123)
    show_selected_options({2: Option('Pray', [], detail=detail)})
    assert '3. Pray' in '\n'.join(lines)
    assert resolve_text(detail) in '\n'.join(lines)


# Exercise real event menus in both languages and both ascension regimes.
# Neow and We Meet Again already put their full effects in option names.
EVENT_MODULES = sorted(p.stem for p in (Path(__file__).parents[1] / 'events').glob('*.py')
                       if p.stem not in {'__init__', 'base_event', 'combat_event', 'event_pool',
                                         'neo_event', 'we_meet_again', 'match_and_keep'})


@pytest.mark.parametrize('module_name', EVENT_MODULES)
@pytest.mark.parametrize('language,ascension', [('en', 0), ('zh', 15)])
def test_event_menus_resolve_effects_without_placeholders(player, module_name, language, ascension):
    set_language(language)
    game_state.ascension = ascension
    game_state.current_floor = 38
    player.card_manager.piles['deck'] = [Strike()]
    from relics.global_relics.event import GoldenIdol, NlothGift
    player.relics = [GoldenIdol(), NlothGift()]
    module = importlib.import_module('events.' + module_name)
    event_class = next(cls for _, cls in inspect.getmembers(module, inspect.isclass)
                       if issubclass(cls, Event) and cls is not Event and cls.__module__ == module.__name__)
    options = menu_for(event_class()).options
    for option in options:
        assert option.detail is not None, (module_name, option.name)
        for value in (option.name, option.detail):
            text = resolve_text(value)
            assert text and '{' not in text and 'event_effects.' not in text and 'events.' not in text
        if module_name == 'lab':
            assert str(2 if ascension >= 15 else 3) in resolve_text(option.detail)



@pytest.mark.parametrize('language', ['en', 'zh'])
def test_cli_tui_and_ai_receive_the_same_event_effects(player, monkeypatch, capsys, language):
    from tui.app import SelectionPanel
    set_language(language)
    menu = menu_for(BigFishEvent())
    expected = resolve_text(menu.options[0].detail)
    game_state.config.mode = 'human'
    game_state.config.auto_select = False
    monkeypatch.setattr('builtins.input', lambda *_: '1')
    assert game_state.runtime_context.default_resolve_human_selection(menu.request) == [0]
    assert expected in capsys.readouterr().out
    panel = SelectionPanel()
    assert expected in '\n'.join(panel._build_selection_lines('', menu.options, 1, True))
    seen = []
    def decide(title, option_text, context, max_select):
        seen.extend(option_text)
        return [0]
    monkeypatch.setattr(game_state, 'decision_engine', SimpleNamespace(make_decision=decide))
    game_state.config.mode = 'ai'
    assert game_state.runtime_context.default_resolve_ai_selection(menu.request) == [0]
    assert expected in seen[0]
