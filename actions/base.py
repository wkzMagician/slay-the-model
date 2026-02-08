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


class Action(Localizable):
    """Base action class - executable game logic unit"""
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Execute this action - to be overridden

        Returns:
            BaseResult: The result of this action execution.
                NoneResult: Action completed with no follow-up
                SingleActionResult: One action to queue next (includes UI selection via SelectAction)
                MultipleActionsResult: Multiple actions to queue next
                GameStateResult: Game state transition (DEATH/WIN)

        """
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}()"

class LambdaAction(Action):
    """Action that executes a provided function"""
    def __init__(self, func, args=None, kwargs=None):
        super().__init__()
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        
    def execute(self) -> 'BaseResult':
        """Execute the provided function with arguments"""
        result = self.func(*self.args, **self.kwargs)
        if isinstance(result, BaseResult):
            return result
        return NoneResult()

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
                if game_state.config.debug:
                    print(f"Executing action: {action}")
            except ImportError:
                pass  # Debug mode not available

            result = action.execute()
            if result is not None:
                # If action returned a result (BaseResult subclass), return it
                if hasattr(result, 'result_type'):
                    return result

            return NoneResult()
        return NoneResult()

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
