"""Flying power for Byrd-like aerial behavior."""
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class FlyingPower(Power):
    """Flying halves incoming damage and loses stacks when hit by attacks."""

    name = "Flying"

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.is_buff = True
        self.is_debuff = False
        self.stack_type = StackType.INTENSITY

    def get_description(self) -> str:
        return (
            f"Take 50% less attack damage. "
            f"Lose 1 stack when hit ({self.amount} stack(s) left)."
        )

    def modify_damage_taken(self, base_damage: int) -> int:
        """Halve incoming damage while Flying has stacks."""
        if self.amount <= 0 or base_damage <= 0:
            return base_damage
        return max(0, int(base_damage * 0.5))

    def on_physical_attack_taken(
        self,
        damage: int,
        source=None,
        card=None,
        player=None,
        damage_type: str = "physical",
    ):
        """Lose Flying on attack hit; ground and stun owner at 0 stacks."""
        if damage <= 0:
            return
        self.amount -= 1
        if self.amount > 0:
            return
        self.amount = 0
        if not self.owner:
            return
        # Byrd stores this as a private field; keep compatibility.
        if hasattr(self.owner, "_is_flying"):
            self.owner._is_flying = False
        if hasattr(self.owner, "is_flying"):
            self.owner.is_flying = False

        # Force current intention to stunned and advance grounded pattern.
        if hasattr(self.owner, "intentions") and "stunned" in self.owner.intentions:
            self.owner.current_intention = self.owner.intentions["stunned"]
        if hasattr(self.owner, "_grounded_pattern_index"):
            current = getattr(self.owner, "_grounded_pattern_index", 0)
            self.owner._grounded_pattern_index = max(1, int(current))
        return
