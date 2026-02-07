"""
Base event definitions for new architecture.
Events use global action queue - they represent random encounters in Unknown Rooms.
"""
from utils.result_types import BaseResult
from engine.game_state import game_state
from localization import Localizable


class Event(Localizable):
    """
    Base event class - represents a random event in Unknown Rooms.
    
    Events are triggered when entering an Unknown Room that resolves
    to an EVENT type. Events can provide rewards, trigger combat,
    or offer choices to the player.
    """
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
        # Control flag for ending event
        self.event_ended = False
    
    def trigger(self) -> 'BaseResult':
        """
        Trigger and execute the event.

        This method should implement the event's main logic,
        building and executing actions as needed.

        Returns:
            BaseResult: The result of this event.
                NoneResult: Event completed with no follow-up
                SingleActionResult: One action to queue next
                MultipleActionsResult: Multiple actions to queue next
                SelectActionResult: UI selection needed
                GameStateResult: Game state transition (DEATH/WIN)
        """
        from utils.result_types import NoneResult
        raise NotImplementedError(f"{self.__class__.__name__} must implement trigger()")
    
    def end_event(self) -> None:
        """End the event and return to room flow"""
        self.event_ended = True
    
    def __str__(self):
        return f"{self.__class__.__name__}()"


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
            is_elite=self.is_elite
        )

        result = combat.start()

        # Handle combat result
        if result == "WIN":
            self._handle_victory()
        elif result == "DEATH":
            # Death is handled by game flow
            pass

        # Convert string result to GameStateResult
        return GameStateResult(result)
    
    def _handle_victory(self):
        """Handle combat victory - add event-specific rewards"""
        # Subclasses can override to add custom rewards
        pass