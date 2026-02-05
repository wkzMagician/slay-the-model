"""
Flex power for Ironclad cards.
Gain temporary Strength at start of turn, lose it at end of turn.
"""
from powers.base import Power
from utils.registry import register
from utils.types import TargetType


@register("power")
class FlexPower(Power):
    """Gain temporary Strength, lose it at end of turn."""
    
    name = "Flex"
    description = "Gain Strength. Lose equal amount at end of turn."
    trigger_timing = "turn_start"
    target_type = TargetType.SELF
    stackable = False  # Flex doesn't stack, replaces existing
    duration = 1  # Lasts 1 turn
    
    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        """
        Args:
            amount: Strength to gain (default 2, upgraded 4)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_player_turn_start(self, player, entities) -> None:
        """Add Strength at start of player's turn."""
        self.owner = player
        self._apply_amount()
    
    def on_player_turn_end(self, player, entities) -> None:
        """Remove Strength at end of player's turn."""
        self._remove_amount()
    
    def _apply_amount(self) -> None:
        """Apply Strength bonus to damage calculations."""
        # Strength is handled by checking powers in on_damage_dealt
        pass
    
    def _remove_amount(self) -> None:
        """Remove Strength bonus."""
        # Strength is handled by removing this power
        if self.owner:
            self.owner.remove_power(self.name)
    
    def on_damage_dealt(self, damage: int, target: any = None,
                      source: any = None, card: any = None) -> int:
        """Modify damage dealt based on temporary Strength."""
        return damage + self.amount
    
    def tick(self) -> None:
        """Decrease duration by 1 turn."""
        if self.duration is not None and self.duration > 0:
            self.duration -= 1
            return self.duration <= 0
        return False
