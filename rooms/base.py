"""
Base room definitions for new architecture.
Rooms use global action queue and lifecycle management.
"""
from actions.base import Action, ActionQueue
from actions.map_selection import SelectMapNodeAction
from utils.result_types import BaseResult
from localization import Localizable
from utils.types import RoomType


class Room(Localizable):
    """Base room class - represents a location where events occur
    
    Rooms use the global action queue for action management.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
        # Control flag for leaving room
        self.should_leave = False
        
        # Room type tracking
        self.room_type = None
        
        # Action queue for room actions
        self.action_queue = ActionQueue()
    
    def init(self):
        """
        Initialize the room - called before enter().
        
        Subclasses should override this method to perform
        room-specific initialization (e.g., generating items, enemies).
        """
        pass
    
    def enter(self) -> BaseResult:
        """
        Enter room and execute room logic.

        This method should implement room's main logic loop,
        building and executing actions as needed.

        Returns:
            Execution result: NoneResult()/"DEATH"/"WIN"
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement enter()")
    
    def leave(self):
        """
        Leave room - perform cleanup.

        Called when player exits the room.
        Clears the global action queue and prepares for next room.
        """
        from engine.game_state import game_state
        
        # Clear global action queue
        game_state.action_queue.clear()

        # Clear event stack in game state
        game_state.event_stack.clear()

        # Reset leave flag
        self.should_leave = False
