"""
Confused power for SneckoEye relic.
Randomizes card costs whenever a card is drawn.
"""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class ConfusedPower(Power):
    """Randomize card costs whenever a card is drawn."""

    name = "Confused"
    description = "Randomize the cost of cards whenever they are drawn."
    stack_type = StackType.PRESENCE
    is_buff = False  # Technically not a buff (unpredictable costs)

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """
        Args:
            amount: Not used for confused (effect is independent of amount)
            duration: 0 for permanent (lasts entire combat)
            owner: The creature that has this power
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_draw(self, card):
        """Complete the original cost update during the draw callback."""
        if card._cost < 0:
            return
        randomized_cost = cast(StreamRandom, get_rng("card_random")).random_int(3)
        if card._cost != randomized_cost:
            card._cost = randomized_cost
            card.cost_until_end_of_turn = randomized_cost
        card.cost_until_played = None
