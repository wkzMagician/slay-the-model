"""PWR-040: revive through real enemy phases and player-turn scheduling.

HP, energy and card inputs are prepared; effects and intentions are never
replaced or invoked directly. Original Darkling.getMove/takeTurn requires
Regrowing followed by Reincarnate while another linked Darkling survives.
"""

import random

import pytest

from actions.combat_cards import PlayCardAction
from cards.ironclad.bludgeon import Bludgeon
from cards.ironclad.cleave import Cleave
from cards.ironclad.strike import Strike
from cards.silent.corpse_explosion import CorpseExplosion
from cards.silent.deadly_poison import DeadlyPoison
from cards.watcher.vault import Vault
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from enemies.act3.darkling import Darkling
from engine.messages import CreatureDiedMessage, EnemyHpDepletedMessage, FatalDamageMessage
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState


def setup(ascension, enemy_class=Darkling, *, natural=False):
    random.seed(523)
    helper = create_test_helper()
    player = helper.create_player(
        hp=80 if natural else 1000,
        max_hp=80 if natural else 1000,
        energy=3 if natural else 30,
    )
    player.base_draw_count = 0
    helper.game_state.ascension = ascension
    target = enemy_class()
    anchor = Darkling() if enemy_class is Darkling else Cultist()
    target.hp = 1
    if not natural:
        target._max_hp = 20
        anchor._max_hp = 1000
        anchor.hp = 1000
    combat = helper.start_combat([target, anchor])
    helper.game_state.drive_actions()
    return helper, combat, target, anchor


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


def next_player(helper, combat):
    combat._start_player_turn()
    helper.game_state.drive_actions()


def observe(helper, monkeypatch):
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return messages


def count(messages, message_class, target):
    return sum(
        isinstance(message, message_class)
        and getattr(message, "creature", getattr(message, "target", None)) is target
        for message in messages
    )


@pytest.mark.parametrize("ascension", [0, 19])
@pytest.mark.parametrize("kind", ["attack", "poison"])
def test_natural_darkling_reincarnates_after_regrowing(ascension, kind):
    helper, combat, target, anchor = setup(ascension, natural=True)
    initial_anchor_hp = anchor.hp
    max_hp = target.max_hp
    play(helper, Strike() if kind == "attack" else DeadlyPoison())
    if kind == "attack":
        assert target.half_dead
        assert target.current_intention is not None
        assert target.current_intention.name == "Regrowing..."
    # Poison kills at the beginning of this enemy phase; either path then
    # performs Regrowing rather than reviving immediately.
    assert combat.execute_enemy_phase() is None
    assert target.hp == 0 and target.half_dead
    next_player(helper, combat)
    assert target.current_intention is not None
    assert target.current_intention.name == "Reincarnate"
    assert target.hp == 0 and target.half_dead
    assert combat.execute_enemy_phase() is None
    assert target.hp == max_hp // 2
    assert not target.half_dead and not target.is_dead()
    assert anchor.hp == initial_anchor_hp
    assert helper.game_state.player.hp > 0
    next_player(helper, combat)
    assert target.current_intention is not None
    assert target.current_intention.name not in {"Regrowing...", "Reincarnate"}


@pytest.mark.parametrize("ascension", [0, 19])
@pytest.mark.parametrize("stacks", [1, 2])
@pytest.mark.parametrize("kind", ["attack", "poison"])
def test_revival_rearms_collapse_and_corpse_explosion(ascension, stacks, kind, monkeypatch):
    helper, combat, target, anchor = setup(ascension)
    messages = observe(helper, monkeypatch)
    for _ in range(stacks):
        play(helper, CorpseExplosion())
    if kind == "attack":
        play(helper, Strike())
    assert combat.execute_enemy_phase() is None
    assert target.hp == 0 and target.half_dead
    assert anchor.hp == 1000 - 20 * stacks
    assert count(messages, EnemyHpDepletedMessage, target) == 1
    assert count(messages, CreatureDiedMessage, target) == 0
    assert count(messages, FatalDamageMessage, target) == 0

    next_player(helper, combat)
    assert combat.execute_enemy_phase() is None
    assert target.hp == 10 and not target.half_dead
    assert target.get_power("Poison") is None
    assert target.get_power("Corpse Explosion") is None
    next_player(helper, combat)
    # A second genuine poison application uses a new corpse-explosion amount.
    for _ in range(2):
        play(helper, CorpseExplosion())
    corpse_explosion = target.get_power("Corpse Explosion")
    assert corpse_explosion is not None and corpse_explosion.amount == 2
    old_hp, old_block = anchor.hp, anchor.block
    play(helper, Bludgeon())
    assert target.hp == 0 and target.half_dead
    assert anchor.hp == old_hp - max(0, 40 - old_block)
    assert count(messages, EnemyHpDepletedMessage, target) == 2
    assert count(messages, CreatureDiedMessage, target) == 0
    assert count(messages, FatalDamageMessage, target) == 0
    assert combat._check_combat_end() is None


@pytest.mark.parametrize("ascension", [0, 19])
def test_half_dead_darkling_is_not_a_player_attack_target(ascension):
    helper, combat, target, anchor = setup(ascension)
    play(helper, Strike())
    assert target.half_dead
    assert combat.execute_enemy_phase() is None
    next_player(helper, combat)
    assert target.current_intention is not None
    assert target.current_intention.name == "Reincarnate"
    before = anchor.hp
    block = anchor.block
    # Debug-first target selection must skip the first, half-dead enemy.
    play(helper, Strike())
    assert target.hp == 0 and target.half_dead
    assert anchor.hp == before - max(0, 6 - block)
    assert combat.combat_state.last_card_targets == [anchor]


@pytest.mark.parametrize("ascension", [0, 19])
@pytest.mark.parametrize("pending_reincarnate", [False, True])
def test_all_linked_darklings_die_without_becoming_eligible_for_revival(
    ascension, pending_reincarnate, monkeypatch
):
    helper, combat, target, anchor = setup(ascension)
    anchor.hp = 1
    messages = observe(helper, monkeypatch)
    if pending_reincarnate:
        play(helper, Strike())
        assert combat.execute_enemy_phase() is None
        next_player(helper, combat)
        assert target.current_intention is not None
        assert target.current_intention.name == "Reincarnate"
        # Removing the final living sibling must cancel this prepared revival.
        play(helper, Strike())
    else:
        play(helper, Cleave())
    assert target.is_dead() and anchor.is_dead()
    assert not target.half_dead and not anchor.half_dead
    for enemy in [target, anchor]:
        assert count(messages, CreatureDiedMessage, enemy) == 1
        assert count(messages, EnemyHpDepletedMessage, enemy) == 1
        assert enemy.current_intention is None
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN


@pytest.mark.parametrize("ascension", [0, 19])
def test_awakened_one_keeps_rebirth_when_player_turn_starts_while_half_dead(ascension):
    helper, combat, target, _ = setup(ascension, AwakenedOne)
    play(helper, Strike())
    assert target.hp == 0 and target.half_dead
    next_player(helper, combat)
    assert target.current_intention is not None
    assert target.current_intention.name == "Rebirth"
    assert combat.execute_enemy_phase() is None
    assert target.hp == 20 and not target.half_dead
    assert getattr(target, "_phase") == 2


@pytest.mark.parametrize("ascension", [0, 19])
def test_vault_preserves_regrowing_until_a_real_enemy_turn(ascension):
    helper, combat, target, _ = setup(ascension)
    play(helper, Strike())
    assert target.half_dead
    play(helper, Vault())
    assert combat.combat_state.current_phase == "player_end"
    assert combat._end_player_phase() is None
    # Vault's enemy phase is skipped. Its extra player turn must retain the
    # already displayed Regrowing intention, even for a half-dead enemy.
    assert combat.execute_enemy_phase() is None
    next_player(helper, combat)
    assert target.hp == 0 and target.half_dead
    assert target.current_intention is not None
    assert target.current_intention.name == "Regrowing..."
    assert combat._end_player_phase() is None
    assert combat.execute_enemy_phase() is None
    assert target.hp == 0 and target.half_dead
    assert target.current_intention.name == "Regrowing..."
    # Once a real Regrowing turn finishes, normal scheduling resumes.
    next_player(helper, combat)
    assert target.current_intention is not None
    assert target.current_intention.name == "Reincarnate"
    assert combat._end_player_phase() is None
    assert combat.execute_enemy_phase() is None
    assert target.hp == 10 and not target.half_dead
