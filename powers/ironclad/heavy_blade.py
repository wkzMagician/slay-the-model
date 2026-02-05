"""
Heavy Blade power for Ironclad cards.
Gain temporary Strength that only affects Heavy Blade cards.
"""
from powers.base import Power
from utils.registry import register
from utils.types import TargetType


@register("power")
class HeavyBladePower(Power):
    """Gain temporary Strength for Heavy Blade attacks."""
    
    name = "Heavy Blade"
    description = "Gain Strength. Lose equal amount at end of turn."
    trigger_timing = "on_damage_dealt"
    target_type = TargetType.SELF
    stackable = False  # Doesn't stack, replaces existing
    duration = 1  # Lasts 1 turn
    
    def __init__(self, amount: int = 5, duration: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 5, upgraded 7)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_damage_dealt(self, damage: int, target: any = None,
                      source: any = None, card: any = None) -> int:
        """Modify damage dealt based on Heavy Blade Strength."""
        # Heavy Blade power only adds to damage
        return damage + self.amount
    
    def on_player_turn_end(self, player, entities) -> None:
        """Remove Heavy Blade Strength at end of player's turn."""
        if self.owner:
            self.owner.remove_power(self.name)
    
    def tick(self) -> None:
        """Decrease duration by 1 turn."""
        if self.duration is not None and self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False
