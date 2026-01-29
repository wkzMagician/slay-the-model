"""
Module initialization for game actions
"""
# Import base classes immediately
from actions.base import Action, ActionQueue
from actions.base import action_queue

# Lazy imports to avoid circular dependencies
def _import_actions():
    """Import all action classes when needed"""
    # This function will be called when actions are actually needed
    pass

# Import commonly used actions
from actions.display import DisplayTextAction, SelectAction
from actions.misc import (
    MoveToPositionAction,
    GenerateMapAction,
    StartEventAction,
)
from actions.card import CreateRandomCardAction, RemoveCardAction

# Global action queue

__all__ = [
    # Base classes
    'Action', 'ActionQueue', 'action_queue',

    # Display actions
    'DisplayTextAction', 'SelectAction',

    # Misc actions
    'MoveToPositionAction', 'GenerateMapAction', 'StartEventAction',

    # Card actions
    'CreateRandomCardAction',
    'RemoveCardAction',
]