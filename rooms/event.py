"""
Event room definitions.

Event rooms are rooms where random events occur when player enters.
Events can offer choices, rewards, or challenges based on game state.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from actions.base import LambdaAction
from actions.display import InputRequestAction
from engine.runtime_events import emit_text
from rooms.base import Room
from utils.option import Option
from utils.random import get_random_events
from utils.registry import register
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

    def enter(self):
        """
        Enter event room and directly trigger the random event.

        """
        from engine.game_state import game_state

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
            add_action(InputRequestAction(options=options))
            return None

        if self.available_events and not self.selected_event:
            self.selected_event = self.available_events[0]

        if not self.selected_event:
            self._empty_pool_result()
            return None

        return self._trigger_event(self.selected_event)

    def _trigger_event(self, event):
        """
        Trigger a specific event.

        Args:
            event: The event instance to trigger

        """
        self.triggered_event = event

        if hasattr(event, 'trigger'):
            event.trigger()
            self._sync_leave_state()
            return None

        return None

    def _sync_leave_state(self) -> None:
        """Leave only after the triggered event explicitly ends."""
        event = self.triggered_event
        if event is None:
            return
        if getattr(event, "event_ended", False):
            self.should_leave = True

    def _empty_pool_result(self) -> None:
        """Return the explicit runtime result for an empty event pool."""
        emit_text(
            self.local("empty_pool", default="The room is quiet. Nothing happens.")
        )
        self.should_leave = True
        return None

    def _select_event(self, event):
        self.selected_event = event
        self._trigger_event(event)
        return None
