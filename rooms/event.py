"""
Event room definitions.

Event rooms are rooms where random events occur when player enters.
Events can offer choices, rewards, or challenges based on game state.
"""
from actions.base import LambdaAction
from actions.display import InputRequestAction
from engine.runtime_events import emit_text
from rooms.base import Room
from utils.option import Option
from utils.random import get_random_events
from utils.registry import register
from utils.result_types import BaseResult, GameStateResult, MultipleActionsResult, NoneResult, SingleActionResult
from utils.types import RoomType


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

        selected_events = get_random_events(
            act=game_state.current_act,
            count=1
        )

        if selected_events:
            self.selected_event = selected_events[0]
            self.available_events = selected_events

    def enter(self) -> BaseResult:
        """
        Enter event room and directly trigger the random event.

        Returns:
            Execution result from event or NoneResult
        """
        emit_text(
            self.local("enter", default="You encounter a mysterious event...")
        )

        if self.available_events and len(self.available_events) > 1:
            options = []
            for event in self.available_events:
                options.append(
                    Option(
                        name=event.local("name") if hasattr(event, "local") else str(event),
                        actions=[LambdaAction(func=self._select_event, args=[event])],
                    )
                )
            return MultipleActionsResult([InputRequestAction(options=options)])

        if self.available_events and not self.selected_event:
            self.selected_event = self.available_events[0]

        if not self.selected_event:
            return self._empty_pool_result()

        event_result = self._trigger_event(self.selected_event)
        return self._merge_display_with_result(event_result)

    def _trigger_event(self, event) -> BaseResult:
        """
        Trigger a specific event.

        Args:
            event: The event instance to trigger

        Returns:
            Result from event trigger
        """
        self.triggered_event = event

        if hasattr(event, 'trigger'):
            result = event.trigger()
            self.should_leave = True
            return result

        return NoneResult()

    def _empty_pool_result(self) -> BaseResult:
        """Return the explicit runtime result for an empty event pool."""
        emit_text(
            self.local("empty_pool", default="The room is quiet. Nothing happens.")
        )
        return NoneResult()

    def _select_event(self, event):
        self.selected_event = event
        result = self._trigger_event(event)
        if isinstance(result, GameStateResult):
            return result
        if hasattr(result, 'action'):
            from engine.game_state import game_state
            game_state.action_queue.add_action(result.action, to_front=True)
        elif hasattr(result, 'actions'):
            from engine.game_state import game_state
            game_state.action_queue.add_actions(result.actions, to_front=True)

    def _merge_display_with_result(self, event_result: BaseResult) -> BaseResult:
        """Attach room entry display to event execution result."""
        if isinstance(event_result, GameStateResult):
            return event_result
        return event_result or NoneResult()
