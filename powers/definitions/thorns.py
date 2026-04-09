"""
Thorns power for combat effects.
Deal damage back when attacked.
"""
from engine.runtime_api import add_actions
from typing import Any
from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import DamageType

@register("power")
class ThornsPower(Power):
    """Deal damage back when attacked."""
    
    name = "Thorns"
    description = "When attacked, deal damage back."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - reflects damage
    
    def __init__(self, amount: int = 3, duration: int = -1, owner=None):
        """
        Args:
            amount: Thorns damage to deal (default 3)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_physical_attack_taken(
        self,
        damage: int,
        source: Any = None,
        card: Any = None,
        player: Any = None,
        damage_type: str = "physical",
    ):
        if source is not None:
            add_actions([DealDamageAction(damage=self.amount, target=source, damage_type=DamageType.MAGICAL)])
            return
        return
