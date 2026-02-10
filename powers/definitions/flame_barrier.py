"""
Flame Barrier power for Ironclad.
Gain block, deal damage to enemies that attack.
"""
from typing import List, Any
from powers.base import Power
from actions.combat import DealDamageAction
from utils.registry import register


@register("power")
class FlameBarrierPower(Power):
    """Gain block. Deal damage to enemies that attack you."""

    name = "Flame Barrier"
    description = "Deal damage to enemies that attack you."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used
            duration: Duration in turns
        """
        super().__init__(amount=0, duration=1, owner=owner)

    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None,
                       player: Any = None, damage_type: str = "direct") -> List[Action]:
        """Deal damage to attacker when this creature is attacked."""
        from engine.game_state import game_state

        # Check if the source is a creature (enemy)
        if hasattr(source, 'on_damage_dealt'):
            actions = []
            damage_amount = 5 if self.duration > 0 else 8  # Base 5, upgraded 8

            # Deal damage back to attacker
            actions.append(DealDamageAction(
                damage=damage_amount,
                target=source,
                damage_type="power",
                source=self.owner if self.owner else None,
                card=None
            ))

            # Decrement duration
            self.tick()

            return actions

        return []

    def tick(self) -> bool:
        """Decrease duration by 1. Returns True if power should be removed."""
        if self.duration is not None and self.duration != 0:
            if not isinstance(self.duration, int):
                return False
            self.duration -= 1
            return self.duration <= 0
        return False
