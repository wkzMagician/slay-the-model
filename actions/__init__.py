"""
Module initialization for game actions

Note on ActionQueue in new architecture:
- Each Room, Event, and Combat has its own ActionQueue for isolation
- Actions return other actions to be added to the caller's queue
- This provides clean separation between different game contexts

Action Result Type System:
- Actions can now return standardized BaseResult types for type safety
- Result types include: NoneResult, SingleActionResult, MultipleActionsResult,
   GameStateResult
- Backward compatible with old-style returns (None, Action, List[Action], "DEATH"/"WIN")
"""
# Import base classes immediately
from actions.base import Action, ActionQueue

# Import result type system
from utils.result_types import (
    BaseResult,
    NoneResult,
    SingleActionResult,
    MultipleActionsResult,
    GameStateResult,
)

# Import commonly used actions
from actions.display import DisplayTextAction, SelectAction
from actions.card import RemoveCardAction
from actions.misc import BuyItemAction, OpenChestAction, LeaveRoomAction
from actions.combat import TriggerRelicAction

__all__ = [
    # Base classes
    'Action', 'ActionQueue',

    # Result type system
    'BaseResult',
    'NoneResult',
    'SingleActionResult',
    'MultipleActionsResult',
    'GameStateResult',

    # Display actions
    'DisplayTextAction', 'SelectAction',

    # Card actions
    'RemoveCardAction',

    # Shop actions
    'BuyItemAction',

    # Treasure actions
    'OpenChestAction',

    # Room actions
    'TriggerRelicAction', 'LeaveRoomAction',
]
