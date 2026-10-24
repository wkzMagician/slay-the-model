"""INT-012: one Rebirth, then real phase-two attacks through turn scheduling.

Original AwakenedOne.takeTurn/getMove selects Dark Echo (40) after Rebirth,
then Sludge/Tackle. Inputs are prepared; effects, RNG and AI are not replaced.
Known PWR-004 regeneration heals the player: damage observations include HP
at publication so that later healing cannot hide a missing attack.
"""

import random

import pytest

from actions.combat_cards import PlayCardAction
from cards.ironclad.strike import Strike
from cards.silent.corpse_explosion import CorpseExplosion
from cards.silent.deadly_poison import DeadlyPoison
from cards.watcher.vault import Vault
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from engine.messages import (
    CreatureDiedMessage,
    DamageDealtMessage,
    EnemyHpDepletedMessage,
    FatalDamageMessage,
)
from powers.definitions.strength import StrengthPower
from tests.test_combat_utils import create_test_helper


def setup(ascension, monkeypatch):
    random.seed(523)
    helper = create_test_helper()
    player = helper.create_player(hp=1000, max_hp=1000, energy=30)
    player.base_draw_count = 0
    helper.game_state.ascension = ascension
    boss, anchor = AwakenedOne(), Cultist()
    boss.hp = 1
    anchor._max_hp = 2000
    anchor.hp = 2000
    combat = helper.start_combat([boss, anchor])
    helper.game_state.drive_actions()
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        messages.append((message, player.hp))
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, combat, boss, anchor, messages


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


def next_player(helper, combat):
    combat._start_player_turn()
    helper.game_state.drive_actions()


def count(messages, kind, boss):
    return sum(
        isinstance(message, kind)
        and getattr(message, "creature", getattr(message, "target", None)) is boss
        for message, _ in messages
    )


@pytest.mark.parametrize("ascension", [0, 4, 9, 19])
@pytest.mark.parametrize("cause", ["attack", "poison"])
def test_rebirth_advances_to_dark_echo_and_later_attacks(ascension, cause, monkeypatch):
    helper, combat, boss, _, messages = setup(ascension, monkeypatch)
    expected_max = 320 if ascension >= 9 else 300
    strength = 2 if ascension >= 4 else 0
    assert boss.max_hp == expected_max
    play(helper, Strike() if cause == "attack" else DeadlyPoison())
    if cause == "attack":
        assert boss.hp == 0 and boss.half_dead
        assert boss.current_intention is not None
        assert boss.current_intention.name == "Rebirth"
    assert combat.execute_enemy_phase() is None
    assert boss.hp == expected_max and not boss.half_dead
    assert boss._phase == 2 and boss.history_intentions[-1] == "Rebirth"
    assert count(messages, EnemyHpDepletedMessage, boss) == 1
    assert count(messages, CreatureDiedMessage, boss) == 0

    next_player(helper, combat)
    assert boss.current_intention is not None
    assert boss.current_intention.name == "Dark Echo"
    before = helper.game_state.player.hp
    assert combat.execute_enemy_phase() is None
    hits = [(m, hp) for m, hp in messages if isinstance(m, DamageDealtMessage)
            and m.source is boss and m.target is helper.game_state.player]
    assert len(hits) == 1
    assert hits[0][0].amount == 40 + strength
    assert hits[0][1] == before - (40 + strength)
    # Exercise the next three actual turns, including their damage, rather
    # than calling determine_next_intention or individual intentions directly.
    for _ in range(3):
        next_player(helper, combat)
        assert boss.current_intention is not None
        move = boss.current_intention.name
        assert move in {"Tackle", "Sludge"}
        start = len(messages)
        assert combat.execute_enemy_phase() is None
        attacks = [m for m, _ in messages[start:] if isinstance(m, DamageDealtMessage)
                   and m.source is boss and m.target is helper.game_state.player]
        assert [m.amount for m in attacks] == (
            [10 + strength] * 3 if move == "Tackle" else [18 + strength]
        )
    assert boss.history_intentions.count("Rebirth") == 1
    assert boss.history_intentions.count("Dark Echo") == 1


@pytest.mark.parametrize("ascension", [0, 19])
@pytest.mark.parametrize("stacks", [1, 2])
def test_revived_boss_final_death_explodes_and_notifies_once(ascension, stacks, monkeypatch):
    helper, combat, boss, anchor, messages = setup(ascension, monkeypatch)
    play(helper, CorpseExplosion())
    play(helper, Strike())
    assert boss.half_dead and anchor.hp == 2000 - boss.max_hp
    assert count(messages, CreatureDiedMessage, boss) == 0
    assert combat.execute_enemy_phase() is None
    next_player(helper, combat)
    assert boss.current_intention is not None
    assert boss.current_intention.name == "Dark Echo"
    # A prepared strength input allows a genuine card attack to defeat the
    # natural 300/320 HP second form without changing that form's health.
    helper.game_state.player.add_power(StrengthPower(amount=1000, owner=helper.game_state.player))
    for _ in range(stacks):
        play(helper, CorpseExplosion())
    before, block = anchor.hp, anchor.block
    play(helper, Strike())
    assert boss.is_dead() and not boss.half_dead and boss.hp == 0
    assert anchor.hp == before - max(0, boss.max_hp * stacks - block)
    assert count(messages, EnemyHpDepletedMessage, boss) == 2
    assert count(messages, CreatureDiedMessage, boss) == 1
    assert count(messages, FatalDamageMessage, boss) == 1
    history = list(boss.history_intentions)
    boss_hits = sum(isinstance(m, DamageDealtMessage) and m.source is boss for m, _ in messages)
    assert combat.execute_enemy_phase() is None
    next_player(helper, combat)
    assert boss.hp == 0 and boss.is_dead()
    assert boss.history_intentions == history
    assert sum(isinstance(m, DamageDealtMessage) and m.source is boss for m, _ in messages) == boss_hits
    assert boss.history_intentions.count("Rebirth") == 1
    assert count(messages, CreatureDiedMessage, boss) == 1


@pytest.mark.parametrize("ascension", [0, 19])
def test_vault_keeps_pending_rebirth_until_actual_enemy_turn(ascension, monkeypatch):
    helper, combat, boss, _, _ = setup(ascension, monkeypatch)
    play(helper, Strike())
    play(helper, Vault())
    assert combat._end_player_phase() is None
    assert combat.execute_enemy_phase() is None
    next_player(helper, combat)
    assert boss.hp == 0 and boss.half_dead
    assert boss.current_intention is not None
    assert boss.current_intention.name == "Rebirth"
    assert "Rebirth" not in boss.history_intentions
    assert combat._end_player_phase() is None
    assert combat.execute_enemy_phase() is None
    assert boss.hp == boss.max_hp and not boss.half_dead
    next_player(helper, combat)
    assert boss.current_intention is not None
    assert boss.current_intention.name == "Dark Echo"
    assert boss.history_intentions.count("Rebirth") == 1
