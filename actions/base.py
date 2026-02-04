"""
Base action system
"""
from localization import Localizable

class Action(Localizable):
    """Base action class - executable game logic unit"""
    def __init__(self):
        pass

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
            try:
                from engine.game_state import game_state
                if game_state.config.debug:
                    print(f"Executing action: {action}")
            except ImportError:
                pass  # Debug mode not available
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
