"""
Event room definitions.

Event rooms are rooms where random events occur when player enters.
Events can offer choices, rewards, or challenges based on game state.
"""
from typing import List, Optional
from rooms.base import Room
from utils.result_types import BaseResult, NoneResult, GameStateResult, MultipleActionsResult, SingleActionResult
from utils.types import RoomType
from utils.random import get_random_events
from actions.display import DisplayTextAction

class EventRoom(Room):
    """
    Event room - presents random events to the player.
    
    When the player enters an event room, they are presented with one or more
    random events based on game state (floor, act, ascension, etc.).
    The player can then choose which event to engage with.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize event room.
        
        Args:
            **kwargs: Additional room parameters
        """
        super().__init__(**kwargs)
        self.room_type = RoomType.EVENT
        
        # List of available events for this room
        self.available_events: List = []
        
        # The event that was selected and triggered
        self.triggered_event = None
    
    def init(self):
        """
        Initialize event room and generate available events.
        
        Generates a list of available events based on current game state
        including floor number, act, ascension level, and other factors.
        """
        from engine.game_state import game_state
        
        # Get random events based on current floor
        # Can specify count of events and floor range
        event_count = self._get_event_count(game_state.current_floor)
        floor_range = self._get_floor_range(game_state.current_floor)
        
        # Get events from pool
        self.available_events = get_random_events(
            floor=game_state.current_floor,
            count=event_count,
            floors=floor_range
        )
        
        # If no events available, create a fallback event
        if not self.available_events:
            self._create_fallback_event()
    
    def enter(self) -> BaseResult:
        """
        Enter event room and directly trigger a random event.

        Returns:
            Execution result from event or NoneResult
        """
        from engine.game_state import game_state
        from localization import t
        from utils.result_types import MultipleActionsResult
        import random

        # Display room description
        display_action = DisplayTextAction(text=t("rooms.event.enter", default="You encounter a mysterious event..."))

        # Check if we have available events
        if not self.available_events:
            # No events available, just return the display action
            return SingleActionResult(display_action)

        # Randomly select one event to trigger
        selected_event = random.choice(self.available_events)

        # Trigger selected event
        event_result = self._trigger_event(selected_event)

        # If event returned a GameStateResult, return it directly
        if isinstance(event_result, GameStateResult):
            return event_result

        # If event returned a SingleActionResult, combine with display action
        if isinstance(event_result, SingleActionResult):
            return MultipleActionsResult([display_action, event_result.action])

        # If event returned a MultipleActionsResult, combine with display action
        if isinstance(event_result, MultipleActionsResult):
            return MultipleActionsResult([display_action] + event_result.actions)

        # If event returned NoneResult, just return the display action
        return SingleActionResult(display_action)
    
    def _get_event_count(self, floor: int) -> int:
        """
        Determine how many events to offer based on floor.
        
        Args:
            floor: Current floor number
            
        Returns:
            Number of events to present
        """
        # Early game: offer 1 event
        if floor <= 4:
            return 1
        # Mid game: offer 2 events
        elif floor <= 10:
            return 2
        # Late game: offer up to 3 events
        else:
            return 3
    
    def _get_floor_range(self, floor: int) -> str:
        """
        Get floor range category for event filtering.
        
        Args:
            floor: Current floor number
            
        Returns:
            Floor range string ('early', 'mid', 'late', 'boss')
        """
        if floor <= 4:
            return 'early'
        elif floor <= 10:
            return 'mid'
        elif floor <= 15:
            return 'late'
        else:
            return 'boss'
    
    def _trigger_event(self, event) -> BaseResult:
        """
        Trigger a specific event.
        
        Args:
            event: The event instance to trigger
            
        Returns:
            Result from event trigger
        """
        from engine.game_state import game_state
        
        # Mark the triggered event
        self.triggered_event = event
        
        # Execute event's trigger method
        if hasattr(event, 'trigger'):
            result = event.trigger()
            
            # Mark room as ready to leave after event completes
            self.should_leave = True
            
            return result
        
        return game_state.execute_all_actions()
    
    def _create_fallback_event(self):
        """
        Create a fallback event when no events are available.

        This ensures that room always has something to offer.
        """
        # Create a simple fallback event that just gives some gold
        from events.base_event import Event
        from utils.result_types import SingleActionResult

        class FallbackEvent(Event):
            def trigger(self):
                from engine.game_state import game_state
                from localization import t
                from actions.display import DisplayTextAction

                gold_gain = 10 + (game_state.current_floor * 5)
                game_state.player.gold += gold_gain

                return SingleActionResult(
                    DisplayTextAction(text=t("rooms.event.fallback",
                                         default=f"You found {gold_gain} gold!"))
                )

        self.available_events = [FallbackEvent()]
