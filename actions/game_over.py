"""Game over action."""

from actions.base import Action
from utils.result_types import GameStateResult, ResultType


class GameOverAction(Action):
    """Action that ends the game with a death result."""
    
    def execute(self) -> GameStateResult:
        """End the game.
        
        Returns:
            GameStateResult with DEATH result type
        """
        return GameStateResult(ResultType.DEATH)
