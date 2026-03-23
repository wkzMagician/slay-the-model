"""
Mayhem power for combat effects.
Play top card of draw pile at start of turn.
"""
from typing import List
from actions.base import Action
from actions.combat import PlayCardAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class MayhemPower(Power):
    """Play top card of draw pile at start of turn."""

    name = "Mayhem"
    description = "Play top card of draw pile at start of turn."
    stack_type = StackType.PRESENCE
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used
            duration: 0 for permanent (this combat)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self) -> List[Action]:
        """Play top card of draw pile at start of turn."""
        from engine.game_state import game_state

        # Get top card from draw pile
        if game_state.player and hasattr(game_state.player, "card_manager"):
            draw_cards = list(game_state.player.card_manager.get_pile("draw_pile"))
            if draw_cards:
                top_card = draw_cards[0]  # ? First card is top
                return [PlayCardAction(card=top_card, is_auto=True, ignore_energy=True)]

        return []
