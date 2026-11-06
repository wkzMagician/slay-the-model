"""Group two: Ritual timing, Spike Slimes, Dead Adventurer, and cleansing."""
from engine.random_streams import get_rng, StreamRandom
from typing import cast

import pytest

from actions.combat import ApplyPowerAction
from actions.display import InputRequestAction
from cards.colorless.ascenders_bane import AscendersBane
from cards.colorless.curse_of_the_bell import CurseOfTheBell
from cards.colorless.doubt import Doubt
from cards.colorless.injury import Injury
from cards.colorless.necronomicurse import Necronomicurse
from cards.colorless.slimed import Slimed
from enemies.act1.cultist import Cultist
from enemies.act1.gremlin_nob import GremlinNob
from enemies.act1.lagavulin import Lagavulin
from enemies.act1.sentry import Sentry
from enemies.act1.spike_slime import SpikeSlimeL, SpikeSlimeM, SpikeSlimeS
from engine.combat import Combat
from engine.game_state import game_state
from events.dead_adventurer import DeadAdventurer
from events.divine_fountain import DivineFountain
from localization import set_language
from potions.global_potions import CultistPotion
from powers.definitions.ritual import RitualPower
from relics.global_relics.boss import SacredBark
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState


def queued_choice() -> InputRequestAction:
    requests = [cast(InputRequestAction, action) for action in game_state.action_queue.queue if isinstance(action, InputRequestAction)]
    assert len(requests) == 1
    game_state.action_queue.clear()
    return requests[0]


@pytest.mark.parametrize('ascension,hp_range,ritual_amount', [
    (0, (48, 54), 3), (1, (48, 54), 3), (2, (48, 54), 4),
    (6, (48, 54), 4), (7, (50, 56), 4), (16, (50, 56), 4), (17, (50, 56), 5),
])
@pytest.mark.parametrize('upper', [False, True])
def test_cultist_hp_and_ritual_ascension_boundaries(monkeypatch, ascension, hp_range, ritual_amount, upper):
    game_state.ascension = ascension
    monkeypatch.setattr(get_rng("monster_hp"), "randint", lambda low, high: high if upper else low)
    enemy = Cultist()
    assert enemy.hp == hp_range[1 if upper else 0]
    enemy.intentions['ritual'].execute()
    game_state.drive_actions()
    ritual = enemy.get_power('Ritual')
    assert ritual is not None
    assert ritual.amount == ritual_amount
    assert ritual.duration == -1
    assert enemy.strength == 0


@pytest.mark.parametrize('ascension,amount', [(0, 3), (2, 4), (17, 5)])
def test_cultist_ritual_skips_initial_round_then_grows_after_attack(ascension, amount):
    helper = create_test_helper()
    player = helper.create_player(hp=80)
    game_state.ascension = ascension
    enemy = Cultist()
    combat = helper.start_combat([enemy])
    expected_hp = 80
    for turn in range(3):
        combat._start_player_turn()
        game_state.drive_actions()
        assert enemy.current_intention is not None
        assert enemy.current_intention.name == ('ritual' if turn == 0 else 'attack')
        combat._end_player_phase()
        # Player turn end must not grant Strength to enemy Ritual.
        assert enemy.strength == max(0, turn - 1) * amount
        combat.execute_enemy_phase()
        if turn:
            expected_hp -= 6 + (turn - 1) * amount
        assert player.hp == expected_hp
        assert enemy.strength == turn * amount


@pytest.mark.parametrize('sacred_bark,amount', [(False, 1), (True, 2)])
def test_cultist_potion_grows_at_player_turn_end_without_round_end_double_trigger(sacred_bark, amount):
    helper = create_test_helper()
    player = helper.create_player()
    if sacred_bark:
        player.relics = [SacredBark()]
    enemy = Cultist()
    combat = helper.start_combat([enemy])
    CultistPotion().on_use([player])
    game_state.drive_actions()
    assert player.strength == 0
    combat._start_player_turn()
    game_state.drive_actions()
    combat._end_player_phase()
    assert player.strength == amount
    combat.execute_enemy_phase()
    assert player.strength == amount
    combat._start_player_turn()
    game_state.drive_actions()
    combat._end_player_phase()
    assert player.strength == 2 * amount


def test_enemy_ritual_stacks_without_resetting_first_round_or_using_amount_as_duration():
    helper = create_test_helper()
    enemy = Cultist()
    combat = helper.start_combat([enemy])
    combat._start_player_turn()
    game_state.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    ApplyPowerAction(RitualPower(amount=2), enemy).execute()
    game_state.drive_actions()
    ritual = enemy.get_power('Ritual')
    assert ritual is not None
    assert ritual.amount == 5
    combat._start_player_turn()
    game_state.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    assert enemy.strength == 5
    strength = enemy.get_power('Strength')
    assert strength is not None
    assert strength.duration == -1


@pytest.mark.parametrize('slime_cls,expected_frail,expected_slimed,damage', [
    (SpikeSlimeM, 1, 1, 10), (SpikeSlimeL, 2, 2, 16),
])
def test_spike_slime_applies_correct_frail_and_adds_slimed_after_damage(slime_cls, expected_frail, expected_slimed, damage):
    helper = create_test_helper()
    player = helper.create_player()
    slime = slime_cls()
    helper.start_combat([slime])
    slime.intentions['lick'].execute()
    game_state.drive_actions()
    frail = player.get_power('Frail')
    assert frail is not None
    assert frail.duration == expected_frail
    slime.intentions['tackle'].execute()
    # Damage is queued before the generated Slimed cards.
    game_state.action_queue.execute_next()  # Expand AttackAction into its damage action.
    game_state.action_queue.execute_next()
    assert player.hp == 80 - damage
    assert player.card_manager.get_pile('discard_pile') == []
    game_state.drive_actions()
    cards = player.card_manager.get_pile('discard_pile')
    assert len(cards) == expected_slimed
    assert all(isinstance(card, Slimed) for card in cards)
    assert player.card_manager.get_pile('hand') == []
    assert player.card_manager.get_pile('deck') == []


def test_small_spike_slime_tackle_does_not_gain_unrelated_status_effects():
    helper = create_test_helper()
    helper.start_combat([SpikeSlimeS()])
    assert game_state.current_combat is not None
    game_state.current_combat.enemies[0].intentions['tackle'].execute()
    game_state.drive_actions()
    assert game_state.player.card_manager.get_pile('discard_pile') == []


@pytest.mark.parametrize('elite_type,expected,count', [
    ('gremlin_nob', GremlinNob, 1), ('lagavulin', Lagavulin, 1), ('sentries', Sentry, 3),
])
@pytest.mark.parametrize('ascension', [0, 18])
def test_dead_adventurer_builds_real_encounters_with_current_ascension(elite_type, expected, count, ascension):
    game_state.ascension = ascension
    event = DeadAdventurer()
    event.elite_type = elite_type
    enemies = event._get_elite_enemies()
    assert len(enemies) == count
    assert all(isinstance(enemy, expected) for enemy in enemies)
    assert all(enemy.ascension == ascension for enemy in enemies)
    if elite_type == 'sentries':
        assert [enemy.is_middle for enemy in enemies] == [False, True, False]


def test_event_lagavulin_preserves_siphon_opening_in_real_turn_flow():
    helper = create_test_helper()
    player = helper.create_player(hp=80)
    event = DeadAdventurer()
    event.elite_type = 'lagavulin'
    enemy = cast(Lagavulin, event._get_elite_enemies()[0])
    combat = helper.start_combat([enemy])
    assert not enemy.is_sleeping
    assert enemy.block == 0
    assert enemy.get_power('Metallicize') is None
    for turn, expected in enumerate(['siphon_soul', 'attack', 'attack', 'siphon_soul']):
        combat._start_player_turn()
        game_state.drive_actions()
        assert enemy.current_intention is not None
        assert enemy.current_intention.name == expected
        combat._end_player_phase()
        combat.execute_enemy_phase()
        assert player.hp == 80 - 18 * min(turn, 2)
    assert player.strength == -2


def test_dead_adventurer_search_starts_fight_and_awards_remaining_loot_once(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = 15
    player.gold = 0
    event = DeadAdventurer()
    event.elite_type = 'lagavulin'
    event.found_relic = True
    fights = []
    def win(combat):
        fights.append(combat.enemies)
        return GameTerminalState.COMBAT_WIN
    monkeypatch.setattr(Combat, 'start', win)
    monkeypatch.setattr(get_rng("misc"), "randint", lambda low, high: low)
    event.trigger()
    request = queued_choice()
    game_state.action_queue.add_actions(request.options[0].actions)
    game_state.drive_actions()
    assert len(fights) == 1
    assert len(fights[0]) == 1
    assert isinstance(fights[0][0], Lagavulin)
    assert event.search_count == 1
    assert event.event_ended
    assert player.gold == 55


@pytest.mark.parametrize('cards,expected', [
    ([], False), ([AscendersBane], False), ([CurseOfTheBell], False), ([Necronomicurse], False),
    ([AscendersBane, CurseOfTheBell, Necronomicurse], False),
    ([Doubt], True), ([AscendersBane, Injury], True),
])
def test_fountain_eligibility_excludes_only_special_curses(cards, expected):
    game_state.player.deck[:] = [cls() for cls in cards]
    assert DivineFountain.can_appear() == expected


def test_fountain_preserves_special_and_bottled_curses_and_uses_normal_remove_hooks(monkeypatch):
    deck = game_state.player.deck
    specials = [AscendersBane(), CurseOfTheBell(), Necronomicurse()]
    bottled = Doubt()
    bottled.bottled = True
    normal = Injury()
    deck[:] = [*specials, bottled, normal]
    removed = []
    monkeypatch.setattr(normal, 'on_remove', lambda: removed.append(normal), raising=False)
    DivineFountain().trigger()
    request = queued_choice()
    for action in request.options[0].actions:
        action.execute()
    game_state.drive_actions()
    assert deck == [*specials, bottled]
    assert removed == [normal]


def test_only_bottled_normal_curse_still_allows_fountain_but_is_not_removed():
    card = Doubt()
    card.bottled = True
    game_state.player.deck[:] = [card]
    assert DivineFountain.can_appear()
    DivineFountain().trigger()
    request = queued_choice()
    assert request.options[0].actions == []
    assert game_state.player.deck == [card]


@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_updated_intentions_and_ritual_descriptions_are_localized(lang):
    set_language(lang)
    enemy = Cultist(ascension=17)
    assert '5' in enemy.intentions['ritual'].description.resolve()
    ritual = RitualPower(amount=5, owner=enemy)
    assert '5' in ritual.local('description').resolve()
    assert '{amount}' not in ritual.local('description').resolve()
    for cls,amount in [(SpikeSlimeM, 1), (SpikeSlimeL, 2)]:
        slime = cls()
        assert str(amount) in slime.intentions['lick'].description.resolve()
        assert str(amount) in slime.intentions['tackle'].description.resolve()
