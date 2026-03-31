"""Defect Rebound power."""

from engine.runtime_api import add_action
from actions.card import MoveCardAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import PilePosType


@register("power")
class ReboundPower(Power):
    name = "Rebound"
    description = "The next card you play this turn is put on top of your draw pile."
    stack_type = StackType.PRESENCE
    is_buff = True

    def on_card_play(self, card, player, targets):
        if self.owner is None:
            return
        add_action(MoveCardAction(card=card, src_pile="discard_pile", dst_pile="draw_pile", position=PilePosType.TOP))
        self.owner.remove_power(self.name)
