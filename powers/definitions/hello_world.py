"""Defect Hello World power."""

from engine.runtime_api import add_action
from actions.card import AddRandomCardAction
from powers.base import Power, StackType
from utils.registry import register
from utils.types import RarityType


@register("power")
class HelloWorldPower(Power):
    name = "Hello World"
    description = "At the start of your turn, add a random Common card into your hand."
    stack_type = StackType.PRESENCE
    is_buff = True

    def on_turn_start(self):
        from engine.game_state import game_state

        namespace = game_state.player.namespace if game_state.player is not None else None
        add_action(AddRandomCardAction(pile="hand", namespace=namespace, rarity=RarityType.COMMON))
