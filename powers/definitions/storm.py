"""Defect Storm power."""

from engine.runtime_api import add_action
from actions.orb import AddOrbAction
from orbs.lightning import LightningOrb
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class StormPower(Power):
    name = "Storm"
    description = "Whenever you play a Power card, Channel {amount} Lightning."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_card_play(self, card, player, targets):
        if getattr(card, "card_type", None) != CardType.POWER:
            return
        for _ in range(self.amount):
            add_action(AddOrbAction(LightningOrb()))
