"""
Room-related actions.
"""
from typing import Optional
from actions.base import Action
from utils.result_types import BaseResult, NoneResult
from utils.registry import register

# todo: 放到别的文件下
@register("action")
class TriggerRelicAction(Action):
    """Trigger a relic's passive or active effect

    Required:
        relic_name (str): Name of the relic to trigger

    Optional:
        None
    """
    def __init__(self, relic_name: str):
        self.relic_name = relic_name

    def execute(self) -> 'BaseResult':
        """Trigger a relic's effect"""
        from engine.game_state import game_state

        if not game_state.player:
            return NoneResult()

        # Find relic
        from utils.registry import get_registered
        relic = get_registered("relic", self.relic_name)
        if not relic:
            return NoneResult()

        # Trigger the relic's effect
        # Relics implement their own trigger logic
        if hasattr(relic, "on_trigger"):
            relic.on_trigger()
        elif hasattr(relic, "passive"):
            relic.passive()

        return NoneResult()

@register("action")
class LeaveRoomAction(Action):
    """Leave a room and return to map state

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Leave a room and return to map state"""
        from engine.game_state import game_state

        # Mark room should leave flag
        if game_state.current_room:
            game_state.current_room.should_leave = True

        return NoneResult()
