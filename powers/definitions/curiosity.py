"""
Curiosity power for enemies.
Gain Strength when the player plays a Power card.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.strength import StrengthPower
from utils.registry import register


@register("power")
class CuriosityPower(Power):
    """Enemy gains Strength whenever the player plays a Power card.
    
    Used by Awakened One boss.
    """
    
    name = "Curiosity"
    description = "Whenever the player plays a Power card, gain 1 Strength."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect for the enemy
    
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Strength to gain per Power card played (default 1)
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets) -> None:
        """Called when a card is played.
        
        If the card is a Power type, gain Strength.
        
        Args:
            card: The card that was played
            player: The player who played the card
            targets: Card play targets
            
        Returns:
            List of actions to execute (ApplyPowerAction for Strength)
        """
        from cards.base import CardType
        
        # Check if the played card is a Power card
        if hasattr(card, 'type') and card.type == CardType.POWER:
            # Gain Strength equal to this power's amount
            from engine.game_state import game_state
            add_actions(
            [ApplyPowerAction(
                target=self.owner,
                power=StrengthPower(amount=self.amount),
                source=self.owner
            )]
            )
            return
        
