"""
Room-related actions.
"""
from typing import Optional
from actions.base import Action
from utils.result_types import BaseResult, NoneResult
from utils.registry import register

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
