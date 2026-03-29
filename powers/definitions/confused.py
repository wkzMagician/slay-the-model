"""
Confused power for SneckoEye relic.
Randomizes card costs whenever a card is drawn.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Optional
from powers.base import Power, StackType
from actions.base import Action, LambdaAction
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
        """Randomize cost of a card when it is drawn.
        
        Args:
            card: The card that was just drawn
            
        Returns:
            List of actions to execute (empty list, effect is immediate)
        """
        import random as rd
        # Randomize between 0 and 3 (like original Slay the Spire)
        # Use LambdaAction to modify card cost via action pattern
        def _randomize_card_cost() -> None:
            randomized_cost = rd.randint(0, 3)
            if hasattr(card.__class__, 'cost') and isinstance(getattr(card.__class__, 'cost'), property):
                setattr(card, '_cost', randomized_cost)
                return
            setattr(card, 'cost', randomized_cost)

        add_actions([LambdaAction(func=_randomize_card_cost)])
        return
