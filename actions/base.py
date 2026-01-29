"""
Base action system
"""
from engine.game_state import game_state

from enum import Enum

class Action:
    """Base action class - executable game logic unit"""

    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {}

    def __init__(self, **kwargs):
        # Remaining kwargs stored for action use
        self.kwargs = kwargs
        self._validate_params()

    def _validate_params(self):
        """Validate required params and inject optional defaults"""
        for name, typ in self.REQUIRED_PARAMS.items():
            if name not in self.kwargs:
                raise ValueError(
                    f"{self.__class__.__name__} missing required param: {name}"
                )
            if typ and not isinstance(self.kwargs[name], typ):
                raise TypeError(f"{name} must be {typ}")

        for name, (typ, default) in self.OPTIONAL_PARAMS.items():
            if name not in self.kwargs:
                self.kwargs[name] = default
            elif typ and not isinstance(self.kwargs[name], typ):
                raise TypeError(f"{name} must be {typ}")

    def execute(self):
        """Execute this action - to be overridden"""
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}()"


class ActionQueue:
    """Queue of actions to execute in loop"""
    def __init__(self):
        self.queue = []

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
        """Execute next action in queue and return result"""
        if self.queue:
            action = self.queue.pop(0)
            if game_state.config.debug:
                print(f"Executing action: {action}")
            result = action.execute()
            return result
        return None

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


# Global action queue
action_queue = ActionQueue()