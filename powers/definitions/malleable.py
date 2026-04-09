# -*- coding: utf-8 -*-
from engine.runtime_api import add_action, add_actions
"""
MalleablePower - Writhing Mass enemy ability
Upon receiving attack damage, gains Block. Block gain increases as triggered.
Resets at the start of turn.
"""
from typing import Any, List
from actions.base import Action
from actions.combat import GainBlockAction
from powers.base import Power, StackType
from localization import LocalStr
from utils.registry import register


@register("power")
class MalleablePower(Power):
    """
    Malleable power for Writhing Mass enemy.
    
    Upon receiving attack damage, gains X Block where X starts at the base amount
    and increases each time it's triggered. Resets at the start of enemy's turn.
    """
    
    name = "Malleable"
    stack_type = StackType.INTENSITY
    is_buff = True
    
    def __init__(self, amount: int = 4, duration: int = -1, owner=None):
        """
        Args:
            amount: Initial block amount to gain (default 4)
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.localization_key = "powers.malleable"
        # Track current block bonus (increases with each trigger)
        self._current_block_bonus = amount
        
    @property
    def current_block(self) -> int:
        """Current block amount to gain on next trigger."""
        return self._current_block_bonus
    
    def on_turn_start(self):
        """Reset block bonus at start of turn."""
        self._current_block_bonus = self.amount

    def on_physical_attack_taken(
        self,
        damage: int,
        source: Any = None,
        card: Any = None,
        player: Any = None,
        damage_type: str = "physical",
    ) -> None:
        """
        Called when owner takes damage.
        Gains block equal to current block bonus, then increases the bonus.
        
        Args:
            damage: Amount of damage taken
            source: Source of the damage
            card: Card that caused damage
            player: Player (not used here)
            damage_type: Type of damage
        """
        if damage > 0 and self.owner:
            block_to_gain = self._current_block_bonus
            # Increase bonus for next trigger
            self._current_block_bonus += 1
            add_actions([GainBlockAction(block_to_gain, self.owner)])

    def local(self, field: str, **kwargs) -> LocalStr:
        """Get localized string for this power."""
        if field == "name":
            return LocalStr(f"{self.localization_key}.name", default=self.name)
        elif field == "description":
            amount = kwargs.get('amount', self.amount)
            current = kwargs.get('current_block', self._current_block_bonus)
            return LocalStr(
                f"{self.localization_key}.description",
                default=f"On damage, gain {current} Block. Increases each trigger. Resets on turn start.",
                amount=amount,
                current_block=current
            )
        return super().local(field, **kwargs)
