"""Producers for automatic original cards and disposable replay copies."""
from typing import TYPE_CHECKING

from actions.base import Action
from utils.registry import register

if TYPE_CHECKING:
    from cards.base import Card


def make_replay_copy(card: "Card") -> "Card":
    """Copy combat values without sharing the card's mutable value containers."""
    clone = card.copy()
    for name, value in vars(card).items():
        if isinstance(value, (dict, list, set)):
            setattr(clone, name, value.copy())
    for name in ("_rebound_to_draw", "_is_replay"):
        if hasattr(clone, name):
            delattr(clone, name)
    return clone


def queue_replay(card: "Card") -> None:
    """Queue one full, free replay, preserving the original target and X."""
    from actions.card_play_lifecycle import queue_card_play
    from engine.game_state import game_state

    combat = game_state.current_combat
    if combat is None:
        return
    targets = list(combat.combat_state.last_card_targets)
    clone = make_replay_copy(card)
    queue_card_play(
        clone, targets=targets, purge=True,
        energy_on_use=int(getattr(card, "_x_cost_energy", 0)), to_front=True,
    )


@register("action")
class PlayTopCardAction(Action):
    """Extract a top card now; its play waits until ordinary actions finish."""

    def __init__(self, exhaust: bool = False):
        self.exhaust = exhaust
        from utils.combat import resolve_target
        from utils.types import TargetType
        # The original producers choose a target while queueing PlayTopCard,
        # before the preceding automatic cards have resolved their damage.
        self.targets = [target for target in resolve_target(TargetType.ENEMY_RANDOM) if target is not None]

    def execute(self) -> None:
        from actions.card_play_lifecycle import queue_card_play
        from engine.game_state import game_state

        player = game_state.player
        if player is None or game_state.current_combat is None:
            return
        cm = player.card_manager
        draw = cm.get_pile("draw_pile")
        if not draw:
            cm.shuffle_discard_to_draw()
            draw = cm.get_pile("draw_pile")
        if not draw:
            return
        card = draw[-1]
        queue_card_play(card, targets=self.targets, exhaust_once=self.exhaust, energy_on_use=player.energy)


@register("action")
class PlayTwiceAction(Action):
    """Play a selected original once, then a separate disposable copy."""

    def __init__(self, card: "Card"):
        self.card = card

    def execute(self) -> None:
        from actions.card_play_lifecycle import queue_card_play
        from engine.game_state import game_state

        if game_state.player is None:
            return
        clone = make_replay_copy(self.card)
        energy = game_state.player.energy
        queue_card_play(self.card, exhaust_once=True, energy_on_use=energy)
        queue_card_play(clone, purge=True, energy_on_use=energy)
