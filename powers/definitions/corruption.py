"""
Corruption power for Ironclad.
Skills cost 0 energy.
"""
from typing import List, TYPE_CHECKING
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class CorruptionPower(Power):
    """Skills cost 0 energy."""

    name = "Corruption"
    description = "Skills cost 0 energy."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used
            duration: 0 for permanent
        """
        super().__init__(amount=0, duration=0, owner=owner)

    def on_draw_card(self, card, player, entities) -> List[Action]:
        """Modify skill costs to 0."""
        from cards.base import Card
        if TYPE_CHECKING:
            from utils.types import CardType

        from engine.game_state import game_state

        # Only affects skills
        if hasattr(card, 'card_type') and card.card_type == CardType.SKILL:
            card.cost = 0

        return []
