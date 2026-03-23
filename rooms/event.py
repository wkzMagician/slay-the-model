"""
Event room definitions.

Event rooms are rooms where random events occur when player enters.
Events can offer choices, rewards, or challenges based on game state.
"""
from actions.display import DisplayTextAction
from rooms.base import Room
from utils.result_types import BaseResult, NoneResult, GameStateResult, MultipleActionsResult, SingleActionResult
from utils.types import RoomType
from utils.random import get_random_events
from utils.registry import register

@register("room")
class EventRoom(Room):
    """
    Event room - presents random events to the player.
    
    When the player enters an event room, a random event is selected
    from the current Act's event pool and triggered directly.
    The player then makes choices within the event itself.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize event room.
        
        Args:
            **kwargs: Additional room parameters
        """
        super().__init__(**kwargs)
        self.room_type = RoomType.EVENT
        
        # The randomly selected event for this room (only one)
        self.selected_event = None
        self.available_events = []
        self.triggered_event = None
    
    def init(self):
        """
        Initialize event room and select a random event.
        
        Selects one random event from the current Act's event pool.
        """
        from engine.game_state import game_state
        import events  # Ensure all @register_event decorators are loaded.
        
        # Get a single random event from the current Act's pool
        selected_events = get_random_events(
            act=game_state.current_act,
            count=1
        )
        
        if selected_events:
            self.selected_event = selected_events[0]
            self.available_events = selected_events
        else:
            # No events available, create a fallback event
            self._create_fallback_event()
    
    def enter(self) -> BaseResult:
        """
        Enter event room and directly trigger the random event.

        Returns:
            Execution result from event or NoneResult
        """
        # Display room description
        display_action = DisplayTextAction(
            text_key="rooms.event.enter",
            default="You encounter a mysterious event...",
        )

        if self.available_events and len(self.available_events) > 1:
            from actions.display import InputRequestAction
            from utils.option import Option
            from actions.base import LambdaAction

            options = []
            for event in self.available_events:
                options.append(
                    Option(
                        name=event.local("name") if hasattr(event, "local") else str(event),
                        actions=[LambdaAction(func=self._select_event, args=[event])],
                    )
                )
            return MultipleActionsResult([display_action, InputRequestAction(options=options)])

        if self.available_events and not self.selected_event:
            self.selected_event = self.available_events[0]

        # Check if we have an event
        if not self.selected_event:
            # No event available, just return the display action
            return SingleActionResult(display_action)

        # Directly trigger the selected event
        event_result = self._trigger_event(self.selected_event)
        return self._merge_display_with_result(display_action, event_result)
    
    def _trigger_event(self, event) -> BaseResult:
        """
        Trigger a specific event.
        
        Args:
            event: The event instance to trigger
            
        Returns:
            Result from event trigger
        """
        # Mark the triggered event
        self.triggered_event = event
        
        # Execute event's trigger method
        if hasattr(event, 'trigger'):
            result = event.trigger()
            
            # Mark room as ready to leave after event completes
            self.should_leave = True
            
            return result

        return NoneResult()
    
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
                from actions.display import DisplayTextAction

                gold_gain = 10 + (game_state.current_floor * 5)
                player = getattr(game_state, "player", None)
                current_gold = getattr(player, "gold", None)
                if isinstance(current_gold, (int, float)):
                    player.gold += gold_gain

                return SingleActionResult(
                    DisplayTextAction(
                        text_key="rooms.event.fallback",
                        default=f"You found {gold_gain} gold!",
                    )
                )

        fallback = FallbackEvent()
        self.selected_event = fallback
        self.available_events = [fallback]

    def _select_event(self, event):
        self.selected_event = event
        result = self._trigger_event(event)
        if isinstance(result, SingleActionResult):
            from engine.game_state import game_state

            game_state.action_queue.add_action(result.action, to_front=True)
        elif isinstance(result, MultipleActionsResult):
            from engine.game_state import game_state

            game_state.action_queue.add_actions(result.actions, to_front=True)

    def _merge_display_with_result(
        self, display_action: DisplayTextAction, event_result: BaseResult
    ) -> BaseResult:
        """Attach room entry display to event execution result."""
        if isinstance(event_result, GameStateResult):
            return event_result
        if isinstance(event_result, SingleActionResult):
            return MultipleActionsResult([display_action, event_result.action])
        if isinstance(event_result, MultipleActionsResult):
            return MultipleActionsResult([display_action] + event_result.actions)
        return SingleActionResult(display_action)
