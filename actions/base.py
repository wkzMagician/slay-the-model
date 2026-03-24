"""
Base action system
"""
from typing import TYPE_CHECKING, List
from localization import Localizable

if TYPE_CHECKING:
    from utils.result_types import (
        BaseResult,
        NoneResult,
    )

from tui.print_utils import tui_print


class Action(Localizable):
    """Base action class - executable game logic unit"""

    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Execute this action - to be overridden

        Returns:
            BaseResult: The result of this action execution.
                NoneResult: Action completed with no follow-up
                SingleActionResult: One action to queue next (includes UI selection via InputRequestAction)
                MultipleActionsResult: Multiple actions to queue next
                GameStateResult: Game state transition (DEATH/WIN)
        """
        raise NotImplementedError

    def _get_localized_key(self, field: str) -> str:
        """Build the localization key for this action field."""
        return f"actions.{self.__class__.__name__}.{field}"


def _get_none_result():
    """Lazy import to avoid circular dependency"""
    from utils.result_types import NoneResult
    return NoneResult()


class LambdaAction(Action):
    """Action that executes a provided function"""

    def __init__(self, func, args=None, kwargs=None):
        super().__init__()
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        
    def execute(self) -> 'BaseResult':
        """Execute the provided function with arguments"""
        from utils.result_types import BaseResult

        result = self.func(*self.args, **self.kwargs)
        if isinstance(result, BaseResult):
            return result
        return _get_none_result()


class ActionQueue:
    """Queue of actions to execute in loop"""

    def __init__(self):
        self.queue: List[Action] = []

    def add_action(self, action, to_front=False):
        """Add action to queue - optionally to front"""
        if to_front:
            self.queue.insert(0, action)
        else:
            self.queue.append(action)

    def add_actions(self, actions, to_front=False):
        """Add multiple actions to queue - optionally to front"""
        if to_front:
            self.queue = actions + self.queue
        else:
            self.queue.extend(actions)

    def execute_next(self):
        """Execute next action in queue and return result

        Returns:
            BaseResult: The result of this action execution.
        """
        if self.queue:
            action = self.queue.pop(0)
            try:
                from engine.game_state import game_state
                if game_state.config.mode == "debug" and game_state.config.debug["print"]:
                    tui_print(f"Executing action: {action}")
            except ImportError:
                pass  # Debug mode not available

            result = action.execute()
            try:
                from engine.runtime_presenter import flush_runtime_events
                flush_runtime_events()
            except ImportError:
                pass
            if result is not None:
                # If action returned a result (BaseResult subclass), return it
                if hasattr(result, 'result_type'):
                    return result

            return _get_none_result()
        return _get_none_result()

    def is_empty(self):
        """Check if queue is empty"""
        return len(self.queue) == 0

    def clear(self):
        """Clear the queue"""
        self.queue = []

    def peek_next(self):
        """Peek at next action without removing it"""
        if self.queue:
            return self.queue[0]
        return None
