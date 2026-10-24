"""Request compatibility and cancellation ownership contracts.

These tests explicitly cancel prepared requests; production autoplay/replay
scenarios are covered separately by test_autoplay_lifecycle.py.
"""

import pickle

import pytest

from actions.base import LambdaAction
from actions.card_play_lifecycle import (
    cancel_pending_card_plays, finalize_card_play, queue_card_play,
)
from actions.combat import EndTurnAction
from actions.combat_cards import PlayCardAction, PlayCardBHAction
from cards.colorless.wound import Wound
from cards.ironclad.defend import Defend
from cards.ironclad.inflame import Inflame
from cards.ironclad.offering import Offering
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from engine.messages import CardExhaustedMessage, CardPlayedMessage
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState


def prepare():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    player.base_draw_count = 0
    enemy = Cultist()
    enemy._max_hp = 100
    enemy.hp = 100
    combat = helper.start_combat([enemy])
    assert helper.game_state.drive_actions() is None
    return helper.game_state, player, enemy, combat


@pytest.mark.parametrize("kind,destination", [
    ("ordinary", "discard_pile"), ("self_exhaust", "exhaust_pile"),
    ("force_exhaust", "exhaust_pile"), ("purge", None),
    ("power_force_exhaust", None),
])
def test_cancelled_request_has_one_destination_and_no_play_event(monkeypatch, kind, destination):
    state, player, _, _ = prepare()
    card = Offering() if kind == "self_exhaust" else Inflame() if kind == "power_force_exhaust" else Wound()
    events = []
    original = state.publish_message

    def publish(message):
        events.append(message)
        original(message)

    monkeypatch.setattr(state, "publish_message", publish)
    request = queue_card_play(card, purge=kind == "purge",
                              exhaust_once=kind in {"force_exhaust", "power_force_exhaust"})
    cancel_pending_card_plays()
    assert state.drive_actions() is None
    assert request.cancelled and request.finalized and not request.started
    assert player.card_manager.get_card_location(card) == destination
    before = len(events)
    finalize_card_play(request)
    assert len(events) == before
    assert not any(isinstance(event, CardPlayedMessage) for event in events)
    assert sum(isinstance(event, CardExhaustedMessage) for event in events) == (destination == "exhaust_pile")
    assert not player.card_manager.get_pile("limbo")


@pytest.mark.parametrize("kind", ["old_prepare", "old_resolved", "direct_resolved"])
def test_legacy_action_without_request_and_direct_resolved_play(kind):
    state, player, enemy, combat = prepare()
    card = Strike()
    player.card_manager.piles["hand"].append(card)
    action = PlayCardAction(card) if kind == "old_prepare" else PlayCardBHAction(card, [enemy])
    if kind != "direct_resolved":
        del action.__dict__["request"]
        action, enemy = pickle.loads(pickle.dumps((action, enemy)))
        combat.enemies = [enemy]
        card = action.card
        player.card_manager.piles["hand"] = [card]
    state.add_action(action)
    assert state.drive_actions() is None
    assert enemy.hp == 94
    assert player.energy == 2
    assert player.card_manager.get_card_location(card) == "discard_pile"
    assert not state.active_card_plays


@pytest.mark.parametrize("phase", ["player_end", "enemy_action", "enemy_end"])
def test_pending_card_cancels_after_player_phase(phase):
    state, player, _, combat = prepare()
    card = Defend()
    request = queue_card_play(card)
    combat.combat_state.current_phase = phase
    assert state.drive_actions() is None
    assert request.cancelled and request.finalized
    assert player.block == 0
    assert player.card_manager.get_card_location(card) == "discard_pile"


def test_end_turn_cancels_pending_without_clearing_effect_actions():
    state, player, _, _ = prepare()
    card = Defend()
    request = queue_card_play(card)
    effects = []
    state.add_actions([EndTurnAction(), LambdaAction(lambda: effects.append("necessary effect"))])
    assert state.drive_actions() is None
    assert effects == ["necessary effect"]
    assert request.cancelled and request.finalized
    assert player.block == 0


@pytest.mark.parametrize("result", [GameTerminalState.GAME_LOSE, GameTerminalState.COMBAT_WIN])
def test_terminal_cleans_active_and_pending_without_running_effects(monkeypatch, result):
    state, player, _, _ = prepare()
    active_card = Offering()
    active_request = queue_card_play(active_card)
    state.pending_card_plays.remove(active_request)
    active_request.started = True
    state.active_card_plays.append(active_request)
    pending_card = Wound()
    pending_request = queue_card_play(pending_card, purge=True)
    effects = []
    monkeypatch.setattr(active_card, "on_exhaust", lambda: effects.append("exhaust hook"))
    state.add_action(LambdaAction(lambda: effects.append("ordinary effect")))
    state.set_terminal_state(result)
    assert state.drive_actions() == result
    assert not effects
    assert not state.active_card_plays and not state.pending_card_plays
    assert active_request.finalized and pending_request.finalized
    assert player.card_manager.get_card_location(active_card) == "exhaust_pile"
    assert player.card_manager.get_card_location(pending_card) is None
    assert not player.card_manager.get_pile("limbo")
    # Existing terminal queue ownership is outside this regression's scope;
    # this change does not clear or execute unrelated queued actions.
    assert not state.action_queue.is_empty()
