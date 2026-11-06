"""
Base event definitions for new architecture.
Events use global action queue - they represent random encounters in Unknown Rooms.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from events.base_event import Event
from utils.result_types import GameTerminalState
from utils.types import CombatType
from localization import Localizable

class CombatEvent(Event):
    """
    Base class for events that trigger combat.
    
    These events lead to combat encounters and then
    return to normal gameplay.
    """
    
    def __init__(self, enemies=None, combat_type=CombatType.NORMAL, **kwargs):
        super().__init__(**kwargs)
        self.enemies = enemies or []
        self.combat_type = combat_type
    
    def trigger(self) -> None:
        """Trigger combat event"""
        from engine.combat import Combat
        from actions.display import DisplayTextAction
        from engine.game_state import game_state

        # Collect all actions
        actions = []

        # Display event description
        actions.append(DisplayTextAction(
            text_key=f"events.{self.__class__.__name__}.description"
        ))

        # Create and start combat
        combat = Combat(
            enemies=self.enemies,
            combat_type=self.combat_type
        )

        result = combat.start()
        
        # Handle combat result
        if result == GameTerminalState.COMBAT_WIN:
            self._handle_victory()
        # ESCAPE：没有reward
        
        if result in (GameTerminalState.GAME_LOSE, GameTerminalState.GAME_EXIT):
            set_terminal_state(result)
            return

        add_actions(actions)
    
    def _handle_victory(self):
        """Handle combat victory - add event-specific rewards"""
        # Subclasses can override to add custom rewards
        pass
