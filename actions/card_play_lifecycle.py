from dataclasses import dataclass
from typing import TYPE_CHECKING
from actions.base import Action

from utils.types import CardType, PilePosType

if TYPE_CHECKING:
    from cards.base import Card
    from entities.creature import Creature


@dataclass
class CardPlayRequest:
    """One use of a card, including cancellation and its single final destination."""

    card: "Card"
    targets: list["Creature"] | None = None
    purge: bool = False
    exhaust_once: bool = False
    energy_on_use: int | None = None
    is_auto: bool = True
    ignore_energy: bool = True
    started: bool = False
    cancelled: bool = False
    finalized: bool = False
    will_exhaust: bool = False


def put_in_limbo(card: "Card") -> None:
    from engine.game_state import game_state

    cm = game_state.player.card_manager
    cm.piles.setdefault("limbo", [])
    location = cm.get_card_location(card)
    if location == "limbo":
        return
    if location is not None and location != "deck":
        cm.remove_from_pile(card, location)
    cm.add_to_pile(card, "limbo", PilePosType.TOP)


def queue_card_play(card: "Card", *, targets: list["Creature"] | None = None,
                    purge: bool = False, exhaust_once: bool = False,
                    energy_on_use: int | None = None, to_front: bool = False) -> CardPlayRequest:
    from engine.game_state import game_state

    request = CardPlayRequest(card, targets, purge, exhaust_once, energy_on_use)
    if purge:
        setattr(card, "_is_replay", True)
    put_in_limbo(card)
    if not hasattr(game_state, "pending_card_plays"):
        game_state.pending_card_plays = []
    if to_front:
        game_state.pending_card_plays.insert(0, request)
    else:
        game_state.pending_card_plays.append(request)
    return request


def finalize_card_play(request: CardPlayRequest, *, trigger_effects: bool = True) -> None:
    from actions.card import DiscardCardAction, ExhaustCardAction
    from engine.game_state import game_state

    if request.finalized:
        return
    request.finalized = True
    card = request.card
    card.cost_until_played = None
    cm = game_state.player.card_manager
    if request.purge:
        location = cm.get_card_location(card)
        if location is not None and location != "deck":
            cm.remove_from_pile(card, location)
        return
    if card.card_type == CardType.POWER:
        location = cm.get_card_location(card)
        if location is not None and location != "deck":
            cm.remove_from_pile(card, location)
        return
    will_exhaust = (request.will_exhaust or request.exhaust_once
                    or card.get_value("exhaust") is True)
    if will_exhaust:
        prevent_exhaust = False
        for relic in game_state.player.relics:
            hook = getattr(relic, "should_prevent_exhaust", None)
            if callable(hook) and hook(card=card):
                prevent_exhaust = True
                break
        if not prevent_exhaust:
            if trigger_effects:
                ExhaustCardAction(card=card).execute()
            else:
                # A terminal driver only restores card ownership; it must not
                # start exhaust-triggered effects after the result is decided.
                cm.exhaust(card, src=None)
            return
    DiscardCardAction(card=card, trigger_effects=False).execute()


def cancel_pending_card_plays() -> None:
    from engine.game_state import game_state

    pending = list(getattr(game_state, "pending_card_plays", []))
    game_state.pending_card_plays = []
    for request in pending:
        request.cancelled = True
        finalize_card_play(request)


class ClearPendingCardPlaysAction(Action):
    """Clear a phase transition's queue without discard/exhaust use hooks."""

    def execute(self) -> None:
        from engine.game_state import game_state

        pending = list(game_state.pending_card_plays)
        game_state.pending_card_plays = []
        cm = game_state.player.card_manager
        for request in pending:
            request.cancelled = True
            request.finalized = True
            if cm.get_card_location(request.card) == "limbo":
                cm.remove_from_pile(request.card, "limbo")


def cleanup_terminal_card_plays() -> None:
    """Finish new card-request ownership without driving post-terminal effects."""
    from engine.game_state import game_state

    active = list(getattr(game_state, "active_card_plays", []))
    pending = list(getattr(game_state, "pending_card_plays", []))
    game_state.active_card_plays = []
    game_state.pending_card_plays = []
    for request in active + pending:
        request.cancelled = True
        finalize_card_play(request, trigger_effects=False)
