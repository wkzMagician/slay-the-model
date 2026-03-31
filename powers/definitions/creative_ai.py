"""Defect Creative AI power."""

from engine.runtime_api import add_action
from actions.card import AddRandomCardAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType


@register("power")
class CreativeAIPower(Power):
    name = "Creative AI"
    description = "At the start of your turn, add a random Power card into your hand."
    stack_type = StackType.PRESENCE
    is_buff = True

    def on_turn_start(self):
        from engine.game_state import game_state

        namespace = game_state.player.namespace if game_state.player is not None else None
        add_action(
            AddRandomCardAction(
                pile="hand",
                namespace=namespace,
                card_type=CardType.POWER,
                exclude_card_ids=["defect.SelfRepair"],
            )
        )
