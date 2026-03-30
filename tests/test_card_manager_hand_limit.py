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


def test_draw_many_overflow_goes_to_discard_pile():
    card_manager = CardManager(deck=[])
    _fill_hand(card_manager)
    overflow = Strike()
    card_manager.add_to_pile(overflow, "draw_pile", PilePosType.TOP)

    drawn = card_manager.draw_many(1)

    assert drawn == [overflow]
    assert len(card_manager.get_pile("hand")) == 10
    assert overflow in card_manager.get_pile("discard_pile")
    assert overflow not in card_manager.get_pile("hand")
