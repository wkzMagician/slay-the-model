"""
Flame Barrier power for Ironclad.
Gain block, deal damage to enemies that attack.
"""
from engine.runtime_api import add_action
from typing import Any
from powers.base import Power, StackType
from actions.combat import DealDamageAction
from utils.registry import register
from utils.types import DamageType


@register("power")
class FlameBarrierPower(Power):
    """Gain block. Deal damage to enemies that attack you."""

    name = "Flame Barrier"
    description = "Deal damage to enemies that attack you."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = 1, owner=None):
        """
        Args:
            amount: Not used
            duration: Duration in turns
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
        """Deal damage to attacker when this creature is attacked."""
        add_action(DealDamageAction(
            damage=self.amount,
            target=source,
            damage_type=DamageType.MAGICAL,
            source=self.owner if self.owner else None,
            card=None
        ))
        return
