"""
Action result type system - unified return types for all actions.

This module defines standard result types that actions can return,
providing type safety and consistent behavior across codebase.
"""
from typing import TYPE_CHECKING, Optional, List, Union
from enum import Enum

if TYPE_CHECKING:
    from actions.base import Action

# Note: Action is imported within TYPE_CHECKING blocks to avoid circular import
# with actions.base which imports from utils.result_types


# ============================================================================
# Result Type Enum
# ============================================================================

class ResultType(str, Enum):
    """Enumeration of result categories for type checking and pattern matching."""
    NONE = "none"
    SINGLE_ACTION = "single_action"
    MULTIPLE_ACTIONS = "multiple_actions"
    GAME_STATE = "game_state"
    INPUT_REQUEST = "input_request"


# ============================================================================
# Base Result Class
# ============================================================================

class BaseResult:
    """Base class for all action result types.

    All actions should return an instance of a subclass of BaseResult
    to provide type safety and consistent handling.

    Attributes:
        result_type (ResultType): The category of this result
    """

    def __init__(self):
        self.result_type: ResultType = ResultType.NONE

    def __str__(self) -> str:
        return f"{self.__class__.__name__}()"


# ============================================================================
# Concrete Result Classes
# ============================================================================

class NoneResult(BaseResult):
    """Result for actions with no follow-up actions (side-effect only).

    This is the most common result type - actions that modify state
    directly without queueing additional actions.

    Example:
        HealAction, GainBlockAction
    """

    def __init__(self):
        super().__init__()
        self.result_type = ResultType.NONE


class SingleActionResult(BaseResult):
    """Result for actions that queue a single follow-up action.

    Used when an action's execution naturally leads to one specific
    next action that should be executed immediately after.

    Attributes:
        action (Action): The action to queue next

    Example:
        AddRandomCardAction, MoveToMapNodeAction, InputRequestAction for UI
    """

    def __init__(self, action: 'Action'):
        super().__init__()
        if TYPE_CHECKING:
            from actions.base import Action
        self.action = action
        self.result_type = ResultType.SINGLE_ACTION

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.action})"


class MultipleActionsResult(BaseResult):
    """Result for actions that queue multiple follow-up actions.

    Used when an action needs to execute several sequential actions,
    typically processed in the order they are provided.

    Attributes:
        actions (List[Action]): List of actions to queue sequentially
    """

    def __init__(self, actions: List['Action']):
        super().__init__()
        if TYPE_CHECKING:
            from actions.base import Action
        self.actions = actions
        self.result_type = ResultType.MULTIPLE_ACTIONS

    def __str__(self) -> str:
        count = len(self.actions)
        return f"{self.__class__.__name__}([{count} actions])"



class GameStateResult(BaseResult):
    """Result for special game state transitions.

    Used for critical game-ending states like combat victory, game victory, 
    combat escape, game loss, or game exit. These results immediately halt 
    action execution and transition to appropriate game state.

    Attributes:
        state (str): Either "COMBAT_WIN", "GAME_WIN", "COMBAT_ESCAPE", 
                     "GAME_LOSE", or "GAME_EXIT"

    Example:
        Combat actions that reduce player HP to 0
        Victory conditions in boss rooms
        Escape mechanics in combat
        Game over conditions
        Game exit (from menu)
    """

    def __init__(self, state: str):
        super().__init__()
        if state not in ("COMBAT_WIN", "GAME_WIN", "COMBAT_ESCAPE", "GAME_LOSE", "GAME_EXIT"):
            raise ValueError(f"GameStateResult must be 'COMBAT_WIN', 'GAME_WIN', 'COMBAT_ESCAPE', 'GAME_LOSE', or 'GAME_EXIT', got: {state}")
        self.state = state
        self.result_type = ResultType.GAME_STATE

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.state})"


class InputRequestResult(BaseResult):
    """Result for pausing action execution until an input request is fulfilled."""

    def __init__(self, request):
        super().__init__()
        self.request = request
        self.result_type = ResultType.INPUT_REQUEST

    def __str__(self) -> str:
        request_type = getattr(self.request, "request_type", "selection")
        return f"{self.__class__.__name__}({request_type})"
