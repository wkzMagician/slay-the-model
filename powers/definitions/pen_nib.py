"""
PenNib power for double damage on every 10th attack.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class PenNibPower(Power):
    """Next attack deals double damage."""
    
    name = "PenNib"
    description = "Next attack deals double damage."
    stackable = True
    is_buff = True
    
    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        """
        Args:
            amount: Multiplier (default 1 for double damage)
            duration: Number of attacks this applies to (default 1)
            owner: Creature with this power
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.damage_multiplier = 2  # Double damage
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """
        Double damage when an attack card is played, then remove self.
        """
        from utils.types import CardType
        
        # Only apply to attack cards
        if card.card_type == CardType.ATTACK:
            # Set card damage to double
            # We modify the card's base damage temporarily
            if hasattr(card, 'base_damage'):
                card.base_damage *= self.damage_multiplier
            
            # After this attack, remove the power (duration decreases)
            self.duration = 0
        
        return []