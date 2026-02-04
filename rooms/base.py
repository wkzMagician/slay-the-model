"""
Base room definitions for the new architecture.
Each room manages its own action queue and lifecycle.
"""
from actions.base import Action, ActionQueue
from actions.map_selection import SelectMapNodeAction
from engine.game_state import game_state
from localization import Localizable
from utils.types import RoomType


class Room(Localizable):
    """Base room class - represents a location where events occur
    
    Each room manages its own action queue and lifecycle independently.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
        # Each room has its own action queue
        self.action_queue = ActionQueue()
        
        # Control flag for leaving the room
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
    
    def enter(self) -> str:
        """
        Enter the room and execute room logic.
        
        This method should implement the room's main logic loop,
        building and executing actions as needed.
        
        Returns:
            Execution result: None/"DEATH"/"WIN"
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement enter()")
    
    def leave(self):
        """
        Leave the room - perform cleanup.
        
        Called when the player exits the room.
        Clears the action queue and prepares for the next room.
        """
        # Clear the action queue
        self.action_queue.clear()
        
        # Clear event stack in game state
        game_state.event_stack.clear()
        
        # Reset leave flag
        self.should_leave = False
    
    def execute_actions(self) -> str:
        """
        Execute all actions in the room's action queue.
        
        This is a helper method for rooms to execute their actions.
        Stops executing when should_leave is True or queue is empty.
        
        Actions can return other Actions or lists of Actions, which will be
        added to the queue automatically.
        
        Returns:
            Execution result if special value encountered, None otherwise
        """
        while not self.should_leave and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            
            # Check if action returned another action to add to queue
            if result is not None:
                if isinstance(result, list):
                    # Add list of actions to front of queue
                    self.action_queue.add_actions(result, to_front=True)
                elif isinstance(result, Action):
                    # Add single action to front of queue
                    self.action_queue.add_action(result, to_front=True)
                # Check for special return values
                elif result in ("DEATH", "WIN"):
                    return result
        
        return None
    
    def add_map_selection_action(self):
        """Add map selection action to queue (for room transitions)"""
        self.action_queue.add_action(SelectMapNodeAction())


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
    
    def enter(self) -> str:
        """Enter the resolved room or event"""
        if self.event:
            # Execute the event
            return self._execute_event()
        elif self.actual_room:
            # Enter the actual room
            return self.actual_room.enter()
        
        # Fallback: nothing to do
        return None
    
    def _resolve_room_type(self) -> RoomType:
        """
        Determine what type this unknown room becomes.
        
        Returns:
            The actual RoomType for this room
        """
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
        if game_state.map_manager:
            return game_state.map_manager._create_room_instance(room_type)
        
        # Fallback: create base room
        return Room()
    
    def _execute_event(self) -> str:
        """Execute the event logic"""
        if self.event:
            # Events in the new architecture have a trigger() method
            if hasattr(self.event, 'trigger'):
                return self.event.trigger()
            else:
                # If event doesn't have trigger(), just return None
                return None
        
        # No event to execute
        return None
