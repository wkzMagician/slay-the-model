"""Game over action."""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from actions.base import Action
from utils.result_types import GameTerminalState


class GameOverAction(Action):
    """Action that ends the game with a death result."""

    preserve_after_combat = True
    
    def execute(self) -> None:
        """End the game."""
        from engine.game_state import game_state

        set_terminal_state(GameTerminalState.GAME_LOSE)
