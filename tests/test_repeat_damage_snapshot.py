"""Repeated effects must snapshot after the original play's effects resolve.

This covers existing Echo Form/Double Tap builders, not the complete autoplay
event protocol (CARD-018/030/031), including Pen Nib/Vigor consumption ordering.
"""

import pytest

from actions.combat_cards import PlayCardAction
from cards.defect.beam_cell import BeamCell
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import DamageDealtMessage
from powers.definitions.double_tap import DoubleTapPower
from powers.definitions.echo_form import EchoFormPower
from powers.definitions.thorns import ThornsPower
from relics.character.ironclad import RedSkull
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState


def prepare(power_type, monkeypatch, hp=100, skull=False, enemy=None):
    helper = create_test_helper()
    player = helper.create_player(hp=hp, max_hp=100, energy=10)
    player.base_draw_count = 0
    if skull:
        player.relics.append(RedSkull())
    enemy = enemy or Cultist()
    enemy._max_hp = 100
    enemy.hp = 100
    helper.start_combat([enemy, Cultist()])
    assert helper.game_state.drive_actions() is None
    power = power_type(amount=1, owner=player)
    player.add_power(power)
    messages = []
    original = helper.game_state.publish_message

    def publish(message, *args, **kwargs):
        if isinstance(message, DamageDealtMessage):
            messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(helper.game_state, "publish_message", publish)
    return helper, player, enemy, power, messages


def play(helper, card):
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_repeat_recalculates_after_first_play_applies_vulnerable(power_type, monkeypatch):
    helper, _, enemy, _, messages = prepare(power_type, monkeypatch)
    assert play(helper, BeamCell()) is None
    assert [m.amount for m in messages if m.target is enemy] == [3, 4]
    assert enemy.hp == 93


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_repeat_recalculates_after_first_play_triggers_red_skull(power_type, monkeypatch):
    helper, player, enemy, _, messages = prepare(power_type, monkeypatch, hp=54, skull=True)
    enemy.add_power(ThornsPower(amount=6, owner=enemy))
    assert play(helper, Strike()) is None
    assert [m.amount for m in messages if m.target is enemy] == [6, 9]
    assert player.hp == 42
    assert player.strength == 3


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_repeat_keeps_source_death_cancellation(power_type, monkeypatch):
    helper, player, enemy, _, messages = prepare(power_type, monkeypatch, hp=3)
    enemy.add_power(ThornsPower(amount=3, owner=enemy))
    assert play(helper, Strike()) == GameTerminalState.GAME_LOSE
    assert player.hp == 0
    assert [m.amount for m in messages if m.target is enemy] == [6]


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_deferred_repeat_preserves_half_dead_source_guard(power_type, monkeypatch):
    helper, player, enemy, power, messages = prepare(power_type, monkeypatch)
    combat = helper.game_state.current_combat
    assert combat is not None
    combat.combat_state.last_card_targets = [enemy]
    # Internal source-state contract: players have no natural half-dead phase.
    # This verifies the deferred builder still reaches the shared source guard.
    power.on_card_play(Strike(), [enemy])
    monkeypatch.setattr(player, "half_dead", True, raising=False)
    assert helper.game_state.drive_actions() is None
    assert not messages
    assert enemy.hp == 100


@pytest.mark.parametrize("power_type", [EchoFormPower, DoubleTapPower])
def test_consumed_repeat_does_not_repeat_following_card(power_type, monkeypatch):
    helper, _, enemy, _, messages = prepare(power_type, monkeypatch)
    assert play(helper, BeamCell()) is None
    assert play(helper, Strike()) is None
    assert [m.amount for m in messages if m.target is enemy] == [3, 4, 9]
