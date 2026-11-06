"""E-02, E-04, E-07: encounter variants, Sentry scaling, and Library access."""
from engine.random_streams import get_rng, StreamRandom
from typing import cast

import pytest

from actions.card import ChooseObtainCardAction
from actions.display import InputRequestAction
from cards.colorless.dazed import Dazed
from enemies.act1.acid_slime import AcidSlimeL
from enemies.act1.sentry import Sentry
from enemies.act1.spike_slime import SpikeSlimeL
from engine.game_state import game_state
from events.event_pool import event_pool
from events.the_library import TheLibrary
from map.encounter_pool import (
    _create_large_slime, _create_sentries, _create_sentry_spheric_guardian,
)
from tests.test_combat_utils import create_test_helper


@pytest.mark.parametrize('roll,expected', [
    (0.0, AcidSlimeL), (0.499999, AcidSlimeL),
    (0.5, SpikeSlimeL), (0.999999, SpikeSlimeL),
])
def test_large_slime_factory_uses_equal_probability_branches(monkeypatch, roll, expected):
    monkeypatch.setattr(get_rng("misc"), "random", lambda: roll)
    enemies = _create_large_slime()
    assert len(enemies) == 1
    assert isinstance(enemies[0], expected)


@pytest.mark.parametrize('ascension,hp_max,damage,dazed', [
    (0, 42, 9, 2), (2, 42, 9, 2), (3, 42, 10, 2),
    (7, 42, 10, 2), (8, 45, 10, 2), (17, 45, 10, 2), (18, 45, 10, 3),
])
def test_sentry_reads_run_ascension_and_applies_thresholds_in_combat(monkeypatch, ascension, hp_max, damage, dazed):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80)
    helper.game_state.ascension = ascension
    monkeypatch.setattr(get_rng("monster_hp"), "randint", lambda low, high: high)
    sentry = Sentry()
    assert sentry.ascension == ascension
    assert sentry.hp == hp_max
    helper.start_combat([sentry])
    sentry.intentions['beam'].execute()
    sentry.intentions['bolt'].execute()
    helper.game_state.drive_actions()
    assert player.hp == 80 - damage
    cards = player.card_manager.get_pile('discard_pile')
    assert len(cards) == dazed
    assert all(isinstance(card, Dazed) for card in cards)


@pytest.mark.parametrize('high_hp,expected_hp', [(False, 38), (True, 42)])
def test_explicit_zero_ascension_overrides_high_run_ascension(monkeypatch, high_hp, expected_hp):
    game_state.ascension = 20
    monkeypatch.setattr(get_rng("monster_hp"), "randint", lambda low, high: high if high_hp else low)
    sentry = Sentry(ascension=0)
    assert sentry.ascension == 0
    assert sentry.hp == expected_hp
    assert getattr(sentry.intentions['beam'], 'base_damage') == 9
    assert getattr(sentry.intentions['bolt'], 'dazed_count') == 2


@pytest.mark.parametrize('factory,expected_middle', [
    (_create_sentries, [False, True, False]),
    (_create_sentry_spheric_guardian, [False]),
])
def test_encounter_factories_inherit_ascension_for_every_sentry(factory, expected_middle):
    game_state.ascension = 18
    sentries = [cast(Sentry, enemy) for enemy in factory() if isinstance(enemy, Sentry)]
    assert [sentry.is_middle for sentry in sentries] == expected_middle
    for sentry in sentries:
        assert sentry.ascension == 18
        assert 39 <= sentry.hp <= 45
        assert getattr(sentry.intentions['beam'], 'base_damage') == 10
        assert getattr(sentry.intentions['bolt'], 'dazed_count') == 3


@pytest.mark.parametrize('ascension', [0, 14, 15, 20])
def test_library_is_available_in_act_two_at_every_ascension(monkeypatch, ascension):
    game_state.ascension = ascension
    metadata = event_pool._event_registry['the_library']
    monkeypatch.setattr(metadata, 'has_been_used', False)
    for act in (1, 2, 3):
        game_state.current_act = act
        available = event_pool.get_available_events(act)
        assert any(entry.event_class is TheLibrary for entry in available) == (act == 2)


@pytest.mark.parametrize('ascension,expected_hp', [(14, 34), (15, 21)])
def test_library_retains_heal_scaling_and_read_choice(ascension, expected_hp):
    helper = create_test_helper()
    player = helper.create_player(hp=1, max_hp=100)
    helper.game_state.ascension = ascension
    TheLibrary().trigger()
    requests = [cast(InputRequestAction, action) for action in helper.game_state.action_queue.queue if isinstance(action, InputRequestAction)]
    assert len(requests) == 1
    request = requests[0]
    assert len(request.options) == 2
    read = cast(ChooseObtainCardAction, request.options[0].actions[0])
    assert isinstance(read, ChooseObtainCardAction)
    assert read.total == 20
    assert not read.can_skip
    helper.game_state.action_queue.clear()
    for action in request.options[1].actions:
        action.execute()
    helper.game_state.drive_actions()
    assert player.hp == expected_hp
