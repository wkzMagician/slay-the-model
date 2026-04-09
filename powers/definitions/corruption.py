"""
Corruption power for Ironclad.
Skills cost 0 energy and exhaust on play.
"""
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class CorruptionPower(Power):
    """Skills cost 0 energy and exhaust when played."""

    name = "Corruption"
    description = "Skills cost 0 energy and exhaust."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used
            duration: 0 for permanent
        """
        super().__init__(amount=0, duration=-1, owner=owner)

    def on_draw_card(self, card):
        """Set drawn skills to 0 cost for the current turn."""
        from utils.types import CardType

        if hasattr(card, 'card_type') and card.card_type == CardType.SKILL:
            card.cost_until_end_of_turn = 0

        return
