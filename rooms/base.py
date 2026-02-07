"""
Base room definitions for new architecture.
Rooms use global action queue and lifecycle management.
"""
from actions.base import Action
from actions.map_selection import SelectMapNodeAction
from utils.result_types import BaseResult, NoneResult, GameStateResult
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

class UnknownRoom(Room):
    """
    Unknown room - resolves to actual room type or event when entered.
    
    This room type exists on the map but resolves its actual content
    when the player enters it, based on game rules and RNG.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.UNKNOWN
        self.actual_room = None  # Resolves to another Room instance
        self.event = None  # Or resolves to an Event instance
    
    def init(self):
        """Initialize and resolve the room type"""
        # Resolve the actual room type
        room_type = self._resolve_room_type()
        
        if room_type == RoomType.EVENT:
            # Resolve to an event
            self.event = self._create_event()
        else:
            # Resolve to another room type
            self.actual_room = self._create_room(room_type)
            # Initialize the actual room
            if self.actual_room:
                self.actual_room.init()
    
    def enter(self) -> BaseResult:
        """Enter resolved room or event"""
        if self.event:
            # Execute event
            return self._execute_event()
        elif self.actual_room:
            # Enter actual room
            return self.actual_room.enter()

        # Fallback: nothing to do
        return NoneResult()
    
    def _resolve_room_type(self) -> RoomType:
        """
        Determine what type this unknown room becomes.

        Returns:
            The actual RoomType for this room
        """
        from engine.game_state import game_state
        # Use map manager's resolution logic
        if game_state.map_manager:
            return game_state.map_manager._resolve_unknown_type(
                game_state.current_floor
            )

        # Fallback: random monster
        return RoomType.MONSTER
    
    def _create_event(self):
        """Create a random event for this room"""
        from events.event_pool import event_pool
        from engine.game_state import game_state

        # Get random event from pool for current floor
        event_class = event_pool.get_random_event(game_state.current_floor)

        if event_class:
            # Create event instance
            event = event_class()

            # Mark unique events as used
            metadata = self._get_event_metadata(event_class)
            if metadata and metadata.is_unique:
                event_pool.mark_event_used(metadata.event_id)

            return event

        return None
    
    def _get_event_metadata(self, event_class):
        """Get metadata for an event class"""
        from events.event_pool import event_pool
        
        # Find metadata by class
        for metadata in event_pool._event_registry.values():
            if metadata.event_class == event_class:
                return metadata
        
        return None
    
    def _create_room(self, room_type: RoomType) -> Room:
        """Create a room instance of the specified type"""
        from engine.game_state import game_state
        if game_state.map_manager:
            return game_state.map_manager._create_room_instance(room_type)

        # Fallback: create base room
        return Room()
    
    def _execute_event(self) -> BaseResult:
        """Execute event logic"""
        if self.event:
            # Events in new architecture have a trigger() method
            if hasattr(self.event, 'trigger'):
                return self.event.trigger()
            else:
                # If event doesn't have trigger(), just return NoneResult
                return NoneResult()

        # No event to execute
        return NoneResult()
