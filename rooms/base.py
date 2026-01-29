"""
Base room definitions for the new architecture.
"""

from actions.base import action_queue
from engine.game_state import game_state

class Room:
    """Base room class - represents a location where events occur"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def enter_room(self):
        """Called when entering this room"""
        pass

    def leave_room(self):
        """Called when leaving this room"""
        # 1. clear all the actions in the action queue
        action_queue.clear()
        # 2. clear all the events in the event stack
        game_state.event_stack.clear()