"""Defect Loop power."""

from engine.runtime_api import add_action
from actions.orb import OrbPassiveAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class LoopPower(Power):
    name = "Loop"
    description = "At the start of your turn, trigger the passive ability of your next Orb {amount} additional time(s)."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_turn_start(self):
        from engine.game_state import game_state

        if game_state.player is None or not game_state.player.orb_manager.orbs:
            return
        orb = game_state.player.orb_manager.orbs[0]
        for _ in range(self.amount):
            add_action(OrbPassiveAction(orb))
