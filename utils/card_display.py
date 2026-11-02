"""Draw-pile view ordering from the original DrawPileViewScreen/CardGroup."""
from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from utils.types import CardType, RarityType

if TYPE_CHECKING:
    from cards.base import Card


# Original AbstractCard.CardRarity declaration order. Project STARTER is BASIC.
_RARITY_ORDER = {rarity: rank for rank, rarity in enumerate((
    RarityType.STARTER, RarityType.SPECIAL, RarityType.COMMON,
    RarityType.UNCOMMON, RarityType.RARE, RarityType.CURSE,
))}


def draw_pile_display_order(cards: Sequence[Card], reveal_order: bool = False) -> list[Card]:
    """Return a view copy; the underlying pile's last element is drawn first.

    Without Frozen Eye, Java's stable name -> rarity -> status-last sorts are
    equivalent to this composite key. Names compare by UTF-16 code units like
    String.compareTo, including localized/upgraded display names.
    """
    ordered = list(reversed(cards))
    if not reveal_order:
        ordered.sort(key=lambda card: (
            card.card_type == CardType.STATUS,
            _RARITY_ORDER.get(card.rarity, len(_RARITY_ORDER)),
            card.display_name.resolve().encode("utf-16-be", errors="surrogatepass"),
        ))
    return ordered
