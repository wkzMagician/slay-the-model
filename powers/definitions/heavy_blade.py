"""
Heavy Blade power for combat effects.
Gain temporary Strength that only affects Heavy Blade cards.
"""
from typing import Any, List
from powers.base import Power
from utils.registry import register


@register("power")
class HeavyBladePower(Power):
    """Gain temporary Strength for Heavy Blade attacks."""
    
    name = "Heavy Blade"
    description = "Gain Strength. Lose equal amount at end of turn."
    stackable = False  # Doesn't stack, replaces existing
    is_buff = True  # Buff - temporary strength for Heavy Blade cards
    
    def __init__(self, amount: int = 5, duration: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 5, upgraded 7)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: Any = None,
                      source: Any = None, card: Any = None) -> List:
        """Modify damage dealt based on Heavy Blade Strength.
        
        Note: The actual damage modification is handled by the combat system
        checking for this power on Heavy Blade cards and reading self.amount.
        """
        # Heavy Blade power only affects Heavy Blade cards
        # The combat system checks the card name and applies this power's amount
        return []
    
    def on_player_turn_end(self, player, entities) -> List:
        """Remove Heavy Blade power at end of player's turn."""
        # Mark for removal - the combat system will handle actual removal
        self.duration = 0
        return []