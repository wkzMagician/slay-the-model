"""Single damage modification, dynamic attack previews, and per-hit resolution."""
from engine.random_streams import get_rng, StreamRandom
import math
from typing import cast

import pytest

from actions.combat import AttackAction, DealDamageAction
from enemies.act2.book_of_stabbing import BookOfStabbing
from enemies.act3.dagger import Dagger
from enemies.act3.darkling import Darkling
from enemies.act3.giant_head import GiantHead
from enemies.act3.nemesis import Nemesis
from enemies.act3.repulsor import Repulsor
from enemies.act3.reptomancer import Reptomancer
from enemies.act3.spiker import Spiker
from enemies.act3.spire_growth import SpireGrowth
from enemies.act3.the_maw import TheMaw
from enemies.act3.transient import Transient
from enemies.act3.writhing_mass import WrithingMass
from engine.game_state import game_state
from localization import LocalStr, set_language
from powers.definitions.intangible import IntangiblePower
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper


CASES = [
    (Dagger, 'Wound', 9, 9, 1),
    (Darkling, 'Nip', 7, 9, 1), (Darkling, 'Chomp', 8, 8, 2),
    (Reptomancer, 'Big Bite', 30, 30, 1), (Reptomancer, 'Snake Strike', 13, 13, 2),
    (TheMaw, 'Slam', 25, 25, 1), (TheMaw, 'Nom Nom', 5, 5, 1),
    (SpireGrowth, 'Quick Tackle', 16, 18, 1), (SpireGrowth, 'Smash', 22, 25, 1),
    (Repulsor, 'Attack', 11, 13, 1), (Spiker, 'Attack', 7, 9, 1),
    (WrithingMass, 'Multi Hit', 7, 8, 3), (WrithingMass, 'Debuff Attack', 10, 11, 1),
    (WrithingMass, 'Big Hit', 32, 35, 1), (WrithingMass, 'Block Attack', 15, 16, 1),
    (Nemesis, 'Tri Attack', 6, 6, 3), (Nemesis, 'Scythe', 45, 45, 1),
]


@pytest.mark.parametrize('enemy_class,key,low,high,hits', CASES)
@pytest.mark.parametrize('ascension', [0, 17])
@pytest.mark.parametrize('strength,weak,vulnerable', [
    (0, False, False), (3, False, False), (0, True, False),
    (0, False, True), (3, True, True), (-4, True, True),
])
def test_attack_preview_and_actual_damage_apply_modifiers_once(
    monkeypatch, enemy_class, key, low, high, hits, ascension, strength, weak, vulnerable,
):
    helper = create_test_helper()
    player = helper.create_player(hp=10000, max_hp=10000)
    game_state.ascension = ascension
    set_language('en')
    monkeypatch.setattr(get_rng("monster_hp"), "randint", lambda low, high: low)
    enemy = enemy_class()
    enemy.add_power(StrengthPower(amount=strength))
    if weak:
        enemy.add_power(WeakPower(duration=2))
    if vulnerable:
        player.add_power(VulnerablePower(duration=2))
    base = high if ascension >= 17 else low
    expected = max(0, math.floor((base + strength) * (0.75 if weak else 1) * (1.5 if vulnerable else 1)))
    intent = enemy.intentions[key]
    preview = cast(LocalStr, intent.description)
    assert intent.get_base_damage() == base
    assert preview.kwargs['damage'] == expected
    if hits > 1:
        assert preview.kwargs['hits'] == hits
    assert str(expected) in str(preview) and '{' not in str(preview)
    intent.execute()
    attacks = [cast(AttackAction, a) for a in game_state.action_queue.queue if isinstance(a, AttackAction)]
    assert len(attacks) == hits
    assert all(a.damage == base for a in attacks)
    game_state.drive_actions()
    assert player.hp == 10000 - expected * hits


def finish_turn(combat):
    combat._end_player_phase()
    combat.execute_enemy_phase()


@pytest.mark.parametrize('ascension,start,rounds', [(1, 30, 5), (2, 40, 5), (16, 40, 5), (17, 40, 6)])
def test_transient_real_turns_grow_after_attacks_and_preserve_fading(ascension, start, rounds):
    helper = create_test_helper()
    player = helper.create_player(hp=2000, max_hp=2000)
    game_state.ascension = ascension
    enemy = Transient()
    combat = helper.start_combat([enemy])
    attack = enemy.intentions['Attack']
    expected_hp = player.hp
    for turn in range(rounds):
        combat._start_player_turn()
        game_state.drive_actions()
        for _ in range(3):
            assert enemy.determine_next_intention() is attack
            assert attack.get_base_damage() == start + turn * 10
            assert cast(LocalStr, attack.description).kwargs['damage'] == start + turn * 10
        finish_turn(combat)
        expected_hp -= start + turn * 10
        assert player.hp == expected_hp
    assert enemy.is_dead()


def test_transient_preview_tracks_temporary_strength_loss():
    helper = create_test_helper()
    player = helper.create_player(hp=1000, max_hp=1000)
    enemy = Transient()
    combat = helper.start_combat([enemy])
    combat._start_player_turn()
    game_state.drive_actions()
    DealDamageAction(damage=12, target=enemy, source=player, damage_type='attack').execute()
    game_state.drive_actions()
    assert cast(LocalStr, enemy.intentions['Attack'].description).kwargs['damage'] == 18
    finish_turn(combat)
    assert player.hp == 982
    assert enemy.strength == 0


@pytest.mark.parametrize('ascension,start,cap', [(2, 30, 60), (3, 40, 70), (17, 40, 70)])
def test_giant_head_next_damage_is_stable_and_caps_in_real_turns(monkeypatch, ascension, start, cap):
    helper = create_test_helper()
    player = helper.create_player(hp=10000, max_hp=10000)
    game_state.ascension = ascension
    monkeypatch.setattr(get_rng("ai"), "random", lambda: 0.9)
    enemy = GiantHead()
    combat = helper.start_combat([enemy])
    time_attacks = 0
    for turn in range(13):
        combat._start_player_turn()
        game_state.drive_actions()
        selected = enemy.current_intention
        assert selected is not None
        for _ in range(3):
            enemy.determine_next_intention()
            assert enemy.current_intention is selected
        damage = selected.get_base_damage()
        if turn >= 4:
            assert selected is enemy.intentions['It Is Time']
            assert damage == min(start + time_attacks * 5, cap)
            assert cast(LocalStr, selected.description).kwargs['damage'] == damage
            time_attacks += 1
        before = player.hp
        finish_turn(combat)
        assert player.hp == before - damage


def test_maw_real_turn_count_uses_original_initial_offset(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=1000, max_hp=1000)
    rolls = iter([0.9, 0.1, 0.1, 0.1, 0.1])
    monkeypatch.setattr(get_rng("ai"), "random", lambda: next(rolls))
    enemy = TheMaw()
    combat = helper.start_combat([enemy])
    enemy.add_power(StrengthPower(amount=3))
    for turn in range(1, 7):
        combat._start_player_turn()
        game_state.drive_actions()
        selected = enemy.current_intention
        assert selected is not None
        for _ in range(3):
            assert enemy.determine_next_intention() is selected
        before = player.hp
        if turn == 1:
            assert selected.name == 'Roar'
        else:
            assert selected.name == 'Nom Nom'
            assert cast(LocalStr, selected.description).kwargs['hits'] == (turn + 1) // 2
        finish_turn(combat)
        assert player.hp == before - (0 if turn == 1 else 8 * ((turn + 1) // 2))


@pytest.mark.parametrize('intangible,block,loss', [(False, 10, 14), (True, 0, 3), (True, 2, 1)])
def test_maw_resolves_each_bite_against_block_and_intangible(intangible, block, loss):
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100)
    enemy = TheMaw()
    intent = enemy.intentions['Nom Nom']
    intent._hits = 3
    enemy.add_power(StrengthPower(amount=3))
    player.block = block
    if intangible:
        player.add_power(IntangiblePower(duration=2))
    intent.execute()
    game_state.drive_actions()
    assert player.hp == 100 - loss
    assert player.block == 0


@pytest.mark.parametrize('ascension,counts', [(17, [2, 3, None, 4]), (18, [2, 3, None, 5])])
def test_book_freezes_hits_before_execution_and_a18_big_stab_growth(monkeypatch, ascension, counts):
    helper = create_test_helper()
    player = helper.create_player(hp=1000, max_hp=1000)
    game_state.ascension = ascension
    monkeypatch.setattr(get_rng("ai"), "random", lambda: 0.9)
    enemy = BookOfStabbing()
    combat = helper.start_combat([enemy])
    for hits in counts:
        combat._start_player_turn()
        game_state.drive_actions()
        selected = enemy.current_intention
        assert selected is not None
        for _ in range(3):
            assert enemy.determine_next_intention(1) is selected
        if hits is not None:
            assert selected.name == 'Multi Stab'
            assert cast(LocalStr, selected.description).kwargs['hits'] == hits
        else:
            assert selected.name == 'Big Stab'
        before = player.hp
        finish_turn(combat)
        assert player.hp == before - (24 if hits is None else 7 * hits)


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_dynamic_and_multi_hit_text_has_no_unfilled_parameters(language):
    helper = create_test_helper()
    helper.create_player()
    set_language(language)
    for enemy, key in [(TheMaw(), 'Nom Nom'), (Darkling(), 'Chomp'),
                       (BookOfStabbing(), 'Multi Stab'), (Transient(), 'Attack'),
                       (GiantHead(), 'It Is Time'), (WrithingMass(), 'Multi Hit')]:
        text = str(enemy.intentions[key].description)
        assert '{' not in text and ' X ' not in text
        assert str(enemy.intentions[key].get_base_damage()) in text
