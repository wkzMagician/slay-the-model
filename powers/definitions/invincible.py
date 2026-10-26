"""
Invincible power for Corrupt Heart.
Caps total HP loss taken each player turn.
"""
from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register


@register("power")
class InvinciblePower(Power):
    """Cap total HP loss taken during a turn and reset at turn start."""

    name = "Invincible"
    description = "Cannot lose more than a fixed amount of HP each turn."
    stack_type = StackType.INTENSITY
    is_buff = True
    modify_phase = DamagePhase.CAPPING
    damage_is_runtime = True

    def __init__(self, amount: int = 300, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.remaining = amount

    def on_turn_start(self):
        self.remaining = self.amount

    def modify_damage_taken(self, base_damage: int) -> int:
        if base_damage <= 0:
            return 0
        return min(base_damage, self.remaining)

    def on_any_hp_lost(self, amount: int, source=None, card=None):
        self.remaining = max(0, self.remaining - int(amount))
