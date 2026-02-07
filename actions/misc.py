"""
Miscellaneous actions
"""
from typing import Optional
from actions.base import Action
from utils.result_types import BaseResult, NoneResult
from localization import t
from utils.registry import register

@register("action")
class StartEventAction(Action):
    """Action to start an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.start_event()
        return NoneResult()
            
@register("action")
class EndEventAction(Action):
    """Action to end an event - inserted to queue head

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.end_event()
        return NoneResult()