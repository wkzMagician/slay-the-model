"""Envenom power for Silent."""

from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.poison import PoisonPower
from utils.registry import register
from utils.types import CardType


@register("power")
class EnvenomPower(Power):
    name = "Envenom"
    description = "Whenever an Attack deals unblocked damage, apply Poison."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_damage_dealt(self, damage: int, target=None, source=None, card=None):
        if damage <= 0 or target is None or getattr(card, 'card_type', None) != CardType.ATTACK:
            return
        from engine.runtime_api import add_actions

        add_actions([
            ApplyPowerAction(PoisonPower(amount=self.amount, duration=self.amount, owner=target), target)
        ])
