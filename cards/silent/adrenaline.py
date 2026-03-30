"""Silent rare skill card - Adrenaline."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Adrenaline(Card):
    """Gain energy and draw cards. Exhaust."""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_draw = 2
    base_energy_gain = 1
    base_exhaust = True

    upgrade_energy_gain = 2
