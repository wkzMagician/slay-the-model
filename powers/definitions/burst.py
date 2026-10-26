"""Burst power for next skill replay."""

from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class BurstPower(Power):
    name = "Burst"
    description = "This turn, your next Skill is played twice."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        if getattr(card, "_is_replay", False) or self.amount <= 0:
            return
        if getattr(card, "card_type", None) != CardType.SKILL:
            return
        from actions.autoplay import queue_replay
        queue_replay(card)
        self.amount -= 1
        if self.owner is not None and self.amount <= 0:
            self.owner.remove_power(self.name)
