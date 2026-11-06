"""INT-001: an opening selection is used once, without a second RNG roll."""
import random
import pytest

from enemies.act1.cultist import Cultist
from enemies.act1.gremlin_nob import GremlinNob
from enemies.act1.sentry import Sentry
from enemies.act1.slime_boss import SlimeBoss
from enemies.act1.the_guardian import TheGuardian
from enemies.act2.bronze_automaton import BronzeAutomaton
from enemies.act2.bronze_orb import BronzeOrb
from enemies.act2.chosen import Chosen
from enemies.act2.byrd import Byrd
from enemies.act2.mystic import Mystic
from enemies.act2.snake_plant import SnakePlant
from enemies.act2.spheric_guardian import SphericGuardian
from enemies.act2.the_champ import TheChamp
from enemies.act2.the_collector import TheCollector
from enemies.act3.dagger import Dagger
from enemies.act3.darkling import Darkling
from enemies.act3.deca import Deca
from enemies.act3.donu import Donu
from enemies.act3.exploder import Exploder
from enemies.act3.giant_head import GiantHead
from enemies.act3.nemesis import Nemesis
from enemies.act3.the_maw import TheMaw
from enemies.act4.corrupt_heart import CorruptHeart
from enemies.act4.spire_shield import SpireShield
from enemies.act4.spire_spear import SpireSpear
from actions.combat import EndTurnAction
from actions.watcher import SkipEnemyTurnAction
from engine.combat import Combat
from tests.test_combat_utils import create_test_helper


def environment(ascension):
    helper = create_test_helper()
    player = helper.create_player(hp=10000, max_hp=10000)
    player.base_draw_count = 0
    gs = helper.game_state
    gs.ascension = ascension
    random.seed(829)
    return helper, gs


FACTORIES = [Cultist, GremlinNob, Sentry, SlimeBoss, TheGuardian,
             BronzeAutomaton, BronzeOrb, Chosen, Mystic, SnakePlant,
             SphericGuardian, TheChamp, TheCollector, Dagger, Darkling,
             Deca, Donu, Exploder, GiantHead, Nemesis, TheMaw,
             CorruptHeart, SpireShield, SpireSpear, Byrd]


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("ascension", [0, 19])
def test_first_player_turn_preserves_selection_and_rng(factory, ascension, monkeypatch):
    helper, gs = environment(ascension)
    enemy = factory()
    calls = []
    native = enemy.determine_next_intention

    def select(*args, **kwargs):
        calls.append(1)
        return native(*args, **kwargs)

    monkeypatch.setattr(enemy, 'determine_next_intention', select)
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    before = enemy.current_intention
    rng = random.getstate()
    assert len(calls) == 1
    combat._start_player_turn()
    gs.drive_actions()
    assert len(calls) == 1
    assert enemy.current_intention is before
    assert random.getstate() == rng


@pytest.mark.parametrize("factory,expected", [
    (Donu, ['Circle of Power', 'Beam', 'Circle of Power', 'Beam']),
    (Deca, ['Beam', 'Square of Protection', 'Beam', 'Square of Protection']),
    (SphericGuardian, ['activate', 'debuff_attack', 'slam', 'harden']),
])
@pytest.mark.parametrize('ascension', [0, 19])
def test_selected_opening_is_not_repeated_next_round(factory, expected, ascension):
    helper, gs = environment(ascension)
    enemy = factory()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    actual = []
    for _ in range(4):
        combat._start_player_turn()
        gs.drive_actions()
        assert enemy.current_intention is not None
        actual.append(enemy.current_intention.name)
        combat._end_player_phase()
        combat.execute_enemy_phase()
    assert actual == expected


@pytest.mark.parametrize('ascension', [0, 19])
def test_three_sentries_keep_position_openings_then_alternate(ascension):
    helper, gs = environment(ascension)
    enemies = [Sentry(is_middle=False), Sentry(is_middle=True), Sentry(is_middle=False)]
    combat = helper.start_combat(enemies)
    gs.drive_actions()
    for wanted in [['bolt', 'beam', 'bolt'], ['beam', 'bolt', 'beam']]:
        combat._start_player_turn()
        gs.drive_actions()
        assert [e.current_intention.name for e in enemies] == wanted
        combat._end_player_phase()
        combat.execute_enemy_phase()


def test_skipping_enemy_turn_does_not_advance_the_unexecuted_opening():
    helper, gs = environment(0)
    enemy = Sentry()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    combat._start_player_turn()
    gs.drive_actions()
    opening = enemy.current_intention
    SkipEnemyTurnAction().execute()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is opening
    assert enemy.turn_count == 1
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is not opening
    assert enemy.turn_count == 2


def test_helper_enemy_phase_before_first_player_phase_does_not_freeze_next_selection():
    helper, gs = environment(0)
    enemy = Sentry()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    opening = enemy.current_intention
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is not opening


def test_bronze_automaton_actually_summons_at_first_enemy_action():
    helper, gs = environment(0)
    boss = BronzeAutomaton()
    combat = helper.start_combat([boss])
    gs.drive_actions()
    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    orbs = [e for e in combat.enemies if isinstance(e, BronzeOrb)]
    assert len(orbs) == 2
    assert all(not orb.history_intentions for orb in orbs)
    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    assert all(len(orb.history_intentions) == 1 for orb in orbs)


def test_native_combat_start_shows_fixed_opening_at_first_decision(monkeypatch):
    helper, gs = environment(0)
    enemy = GremlinNob()
    combat = Combat([enemy])
    seen = []

    class FirstDecisionReached(Exception):
        pass

    def choose(req):
        seen.append(enemy.current_intention.name)
        # Observe the original Combat.start boundary without changing AI,
        # effects or fabricating a combat result.
        raise FirstDecisionReached

    monkeypatch.setattr(gs, 'resolve_input_request', choose)
    with pytest.raises(FirstDecisionReached):
        combat.start()
    assert seen == ['bellow']
