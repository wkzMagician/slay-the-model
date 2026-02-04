"""
Module initialization for game actions

Note on ActionQueue in new architecture:
- Each Room, Event, and Combat has its own action_queue for isolation
- Actions return other actions to be added to the caller's queue
- This provides clean separation between different game contexts
"""
# Import base classes immediately
from actions.base import Action, ActionQueue

# Import commonly used actions
from actions.display import DisplayTextAction, SelectAction
from actions.misc import (
    StartEventAction,
)
from actions.card import RemoveCardAction
from actions.shop import BuyItemAction, CardRemovalAction, LeaveShopAction
from actions.treasure import OpenChestAction, SkipTreasureAction

__all__ = [
    # Base classes
    'Action', 'ActionQueue',

    # Display actions
    'DisplayTextAction', 'SelectAction',

    # Misc actions
    'StartEventAction',

    # Card actions
    'RemoveCardAction',

    # Shop actions
    'BuyItemAction', 'CardRemovalAction', 'LeaveShopAction',

    # Treasure actions
    'OpenChestAction', 'SkipTreasureAction',
]
