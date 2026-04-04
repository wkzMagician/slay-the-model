from player.card_manager import CardManager
from cards.ironclad.strike import Strike
from utils.types import PilePosType


def _fill_hand(card_manager: CardManager, count: int = 10) -> None:
    for _ in range(count):
        card_manager.add_to_pile(Strike(), "hand", PilePosType.TOP)


def test_add_to_hand_overflow_goes_to_discard_pile():
    card_manager = CardManager(deck=[])
    _fill_hand(card_manager)

    overflow = Strike()
    added = card_manager.add_to_pile(overflow, "hand", PilePosType.TOP)

    assert added is True
    assert len(card_manager.get_pile("hand")) == 10
    assert overflow in card_manager.get_pile("discard_pile")


def test_hand_full_no_shuffle_when_draw_empty_and_discard_nonempty():
    """StS checks hand before shuffle: full hand skips refill even if discard has cards."""
    card_manager = CardManager(deck=[])
    _fill_hand(card_manager)
    card_manager.add_to_pile(Strike(), "discard_pile", PilePosType.TOP)

    assert card_manager.draw_many(3) == []
    assert len(card_manager.get_pile("hand")) == 10
    assert len(card_manager.get_pile("draw_pile")) == 0
    assert len(card_manager.get_pile("discard_pile")) == 1


def test_draw_many_skips_when_hand_full():
    """Full hand: do not draw, shuffle, or move draw pile cards (StS DrawCardAction parity)."""
    card_manager = CardManager(deck=[])
    _fill_hand(card_manager)
    overflow = Strike()
    card_manager.add_to_pile(overflow, "draw_pile", PilePosType.TOP)

    drawn = card_manager.draw_many(1)

    assert drawn == []
    assert len(card_manager.get_pile("hand")) == 10
    assert overflow in card_manager.get_pile("draw_pile")
    assert overflow not in card_manager.get_pile("discard_pile")
