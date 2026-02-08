"""
Base event definitions for new architecture.
Events use global action queue - they represent random encounters in Unknown Rooms.
"""
from events.base_event import Event
from utils.result_types import BaseResult
from engine.game_state import game_state
from localization import Localizable

class CombatEvent(Event):
    """
    Base class for events that trigger combat.
    
    These events lead to combat encounters and then
    return to normal gameplay.
    """
    
    def __init__(self, enemies=None, is_elite=False, **kwargs):
        super().__init__(**kwargs)
        self.enemies = enemies or []
        self.is_elite = is_elite
    
    def trigger(self) -> 'BaseResult':
        """Trigger combat event"""
        from engine.combat import Combat
        from actions.display import DisplayTextAction
        from utils.result_types import GameStateResult

        # Display event description
        game_state.action_queue.add_action(DisplayTextAction(
            text_key=f"events.{self.__class__.__name__}.description"
        ))

        # Create and start combat
        combat = Combat(
            enemies=self.enemies,
        )

        result = combat.start()
        
        # Handle combat result
        if result.state == "COMBAT_WIN":
            self._handle_victory()
        # ESCAPE：没有reward
        
        if result.state == "GAME_LOSE":
            return result
        else:
            return game_state.execute_all_actions()
    
    def _handle_victory(self):
        """Handle combat victory - add event-specific rewards"""
        # Subclasses can override to add custom rewards
        pass