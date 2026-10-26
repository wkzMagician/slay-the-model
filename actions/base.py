"""
Base action system
"""
from collections.abc import Callable, Mapping, Sequence
from localization import Localizable

from tui.print_utils import tui_print


class Action(Localizable):
    """Base action class - executable game logic unit"""

    preserve_after_combat = False

    def __init__(self) -> None:
        super().__init__()

    def execute(self) -> None:
        """Execute this action - to be overridden."""
        raise NotImplementedError

    def _get_localized_key(self, field: str) -> str:
        """Build the localization key for this action field."""
        return f"actions.{self.__class__.__name__}.{field}"

class LambdaAction(Action):
    """Action that executes a provided function"""

    def __init__(
        self,
        func: Callable[..., object],
        args: Sequence[object] | None = None,
        kwargs: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__()
        self.func = func
        self.args = list(args) if args is not None else []
        self.kwargs = dict(kwargs) if kwargs is not None else {}
        
    def execute(self) -> None:
        """Execute the provided function with arguments."""
        self.func(*self.args, **self.kwargs)


class ActionQueue:
    """Queue of actions to execute in loop"""

    def __init__(self):
        self.queue: list[Action] = []

    def add_action(self, action: Action, to_front: bool = False) -> None:
        """Add action to queue - optionally to front"""
        if to_front:
            self.queue.insert(0, action)
        else:
            self.queue.append(action)

    def add_actions(self, actions: Sequence[Action], to_front: bool = False) -> None:
        """Add multiple actions to queue - optionally to front"""
        if not actions:
            return
        if to_front:
            self.queue = list(actions) + self.queue
        else:
            self.queue.extend(actions)

    def execute_next(self) -> None:
        """Execute next action in queue."""
        if self.queue:
            action = self.queue.pop(0)
            try:
                from engine.game_state import game_state
                if game_state.config.mode == "debug" and game_state.config.debug.get("print", False):
                    tui_print(f"Executing action: {action}")
            except ImportError:
                pass  # Debug mode not available

            action.execute()
            try:
                from engine.runtime_presenter import flush_runtime_events
                flush_runtime_events()
            except ImportError:
                pass

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.queue) == 0

    def clear(self) -> None:
        """Clear the queue"""
        self.queue = []

    def peek_next(self) -> Action:
        """Peek at next action without removing it."""
        if not self.queue:
            raise IndexError("Action queue is empty")
        return self.queue[0]


def queue_actions(actions: Sequence[Action] | None, to_front: bool = False) -> None:
    """Queue actions on the global action queue when any are provided."""
    if not actions:
        return
    from engine.runtime_api import add_actions

    add_actions(actions, to_front=to_front)


def queue_action(action: Action | None, to_front: bool = False) -> None:
    """Queue one action on the global action queue when provided."""
    if action is None:
        return
    from engine.runtime_api import add_action

    add_action(action, to_front=to_front)
