"""Phantasmal Killer active power."""

from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import CardType


@register("power")
class PhantasmalKillerPower(Power):
    name = "Phantasmal Killer"
    description = "Your attacks deal double damage this turn."
    stack_type = StackType.LINKED
    amount_equals_duration = True
    is_buff = True
    modify_phase = DamagePhase.MULTIPLICATIVE

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        if getattr(card, 'card_type', None) == CardType.ATTACK:
            return base_damage * 2
        return base_damage

    def on_turn_end(self):
        if self.owner is not None:
            if self.tick():
                self.owner.remove_power(self)
