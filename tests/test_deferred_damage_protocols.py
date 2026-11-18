"""Native card and turn-end regressions for deferred random damage."""
from typing import cast

import pytest

from actions.base import LambdaAction
from actions.combat_cards import PlayCardAction
from actions.combat_damage import DealDamageAction, GainBlockAction
from actions.orb import AddOrbAction, EvokeOrbAction
from cards.defect.dualcast import Dualcast
from cards.defect.multi_cast import MultiCast
from cards.ironclad.iron_wave import IronWave
from cards.ironclad.juggernaut import Juggernaut
from enemies.act1.cultist import Cultist
from engine.combat import Combat
from engine.game_state import game_state
from engine.messages import DamageDealtMessage
from engine.random_streams import StreamRandom, get_rng
from orbs.lightning import LightningOrb
from player.player_factory import create_player
from powers.definitions.electro import ElectroPower
from powers.definitions.focus import FocusPower
from powers.definitions.juggernaut import JuggernautPower
from powers.definitions.lock_on import LockOnPower
from powers.definitions.buffer import BufferPower
from powers.definitions.intangible import IntangiblePower
from powers.definitions.thorns import ThornsPower
from tests.test_special_card_reference import trace_rng
from utils.result_types import GameTerminalState


def prepare(role="ironclad", ascension=0, health=(1000, 1000)):
    player = create_player(role, ascension=ascension)
    player.relics.clear()
    player.base_draw_count = 0
    game_state.player = player
    game_state.ascension = ascension
    game_state.config.debug["select_type"] = "first"
    enemies = [Cultist() for _ in health]
    for enemy, hp in zip(enemies, health):
        enemy._max_hp = 1000
        enemy.hp = hp
    combat = Combat(enemies=enemies)
    game_state.combat = combat
    combat._init_combat()
    assert game_state.drive_actions() is None
    for name, pile in player.card_manager.piles.items():
        if name != "deck":
            pile.clear()
    player.energy = 10
    return player, enemies, combat


def play(card):
    game_state.player.card_manager.piles["hand"].append(card)
    game_state.add_action(PlayCardAction(card))
    return game_state.drive_actions()


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("lethal", [False, True])
def test_juggernaut_selects_after_iron_wave_damage(role, ascension, upgraded, lethal, monkeypatch):
    player, enemies, _ = prepare(role, ascension, (5 if lethal else 1000, 1000))
    power_card = Juggernaut()
    if upgraded:
        power_card.upgrade()
    assert play(power_card) is None
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(1)
    original = rng.random_int
    selections = []

    def select(start, end=None):
        selections.append([enemy.hp for enemy in enemies])
        return original(start, end)

    monkeypatch.setattr(rng, "random_int", select)
    assert play(IronWave()) is None
    assert selections == [[0 if lethal else 995, 1000]]
    damage = 7 if upgraded else 5
    if lethal:
        assert [enemy.hp for enemy in enemies] == [0, 1000 - damage]
    else:
        assert sum(enemy.hp for enemy in enemies) == 2000 - 5 - damage
    assert player.block == 5


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("kind", ["dualcast", "turn_end", "multicast", "overflow"])
def test_lightning_finishes_each_hit_before_next_target(role, ascension, kind, monkeypatch):
    hp = 3 if kind == "turn_end" else 8
    count = 3 if kind == "multicast" else 2
    player, enemies, combat = prepare(role, ascension, [hp] * count)
    player.orb_manager.max_orb_slots = 3
    player.orb_manager.orbs[:] = [LightningOrb() for _ in range(2 if kind == "turn_end" else 1)]
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    if kind == "dualcast":
        assert play(Dualcast()) is None
    elif kind == "turn_end":
        assert combat._end_player_phase() is None
    elif kind == "multicast":
        player.energy = 3
        assert play(MultiCast()) is None
    else:
        player.orb_manager.max_orb_slots = 1
        game_state.add_actions([AddOrbAction(LightningOrb()), EvokeOrbAction()])
        assert game_state.drive_actions() is None
        assert player.orb_manager.orbs == []
    assert [enemy.hp for enemy in enemies] == [0] * count
    assert [call[2] for call in calls] == list(range(count - 1, -1, -1))
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN


@pytest.mark.parametrize("focus", [-4, 0, 2])
@pytest.mark.parametrize("hit_all", [False, True])
@pytest.mark.parametrize("evoke", [False, True])
def test_lightning_focus_lock_on_and_electro(focus, hit_all, evoke, monkeypatch):
    player, enemies, _ = prepare()
    player.add_power(FocusPower(amount=focus, owner=player))
    for enemy in enemies:
        enemy.add_power(LockOnPower(amount=1, owner=enemy))
        enemy.block = 1
    if hit_all:
        player.add_power(ElectroPower(owner=player))
    rng = cast(StreamRandom, get_rng("card_random"))
    calls = trace_rng(rng, monkeypatch)
    orb = LightningOrb()
    (orb.on_evoke if evoke else orb.on_passive)()
    assert calls == []
    assert game_state.drive_actions() is None
    damage = max(0, int(max(0, (8 if evoke else 3) + focus) * 1.5) - 1)
    assert sum(1000 - enemy.hp for enemy in enemies) == damage * (2 if hit_all else 1)
    assert len(calls) == (0 if hit_all else 1)


def test_lightning_snapshots_focus_and_electro_but_reads_lock_on_at_execution():
    player, enemies, _ = prepare()
    focus = FocusPower(amount=2, owner=player)
    player.add_power(focus)
    LightningOrb().on_passive()
    focus.amount = 20
    player.add_power(ElectroPower(owner=player))
    for enemy in enemies:
        enemy.add_power(LockOnPower(amount=1, owner=enemy))
    assert game_state.drive_actions() is None
    assert sum(1000 - enemy.hp for enemy in enemies) == 7


def test_juggernaut_zero_block_and_multiple_gains(monkeypatch):
    player, enemies, _ = prepare()
    power = JuggernautPower(amount=5, owner=player)
    player.add_power(power)
    calls = trace_rng(cast(StreamRandom, get_rng("card_random")), monkeypatch)
    power.on_gain_block(0)
    assert game_state.action_queue.is_empty()
    game_state.add_actions([GainBlockAction(1, player), GainBlockAction(2, player)])
    assert game_state.drive_actions() is None
    assert len(calls) == 2
    assert sum(1000 - enemy.hp for enemy in enemies) == 10


def test_electro_matrix_completes_before_queued_damage_reactions(monkeypatch):
    player, enemies, _ = prepare()
    player.add_power(ElectroPower(owner=player))
    observed = []
    original = game_state.publish_message

    def publish(message, *args, **kwargs):
        if isinstance(message, DamageDealtMessage):
            game_state.add_action(LambdaAction(lambda: observed.append([enemy.hp for enemy in enemies])), to_front=True)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", publish)
    LightningOrb().on_passive()
    assert game_state.drive_actions() is None
    assert observed == [[997, 997], [997, 997]]


@pytest.mark.parametrize("kind", ["juggernaut", "passive", "evoke"])
@pytest.mark.parametrize("defense", ["buffer", "intangible", "thorns"])
def test_deferred_damage_uses_live_defenses_and_nonattack_reactions(kind, defense):
    player, enemies, _ = prepare(health=(1000,))
    enemy = enemies[0]
    power_type = {"buffer": BufferPower, "intangible": IntangiblePower, "thorns": ThornsPower}[defense]
    enemy.add_power(power_type(amount=1, owner=enemy))
    player_hp = player.hp
    damage = {"juggernaut": 5, "passive": 3, "evoke": 8}[kind]
    for _ in range(2):
        if kind == "juggernaut":
            JuggernautPower(amount=5, owner=player).on_gain_block(1)
        else:
            orb = LightningOrb()
            (orb.on_passive if kind == "passive" else orb.on_evoke)()
    assert game_state.drive_actions() is None
    expected = damage if defense == "buffer" else 2 if defense == "intangible" else 2 * damage
    assert enemy.hp == 1000 - expected
    assert player.hp == player_hp
