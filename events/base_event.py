"""
Base event definitions for the new architecture.
Events are now simple - they represent random encounters in Unknown Rooms.
"""
from actions.base import ActionQueue
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
        
        # Each event has its own action queue
        self.action_queue = ActionQueue()
        
        # Control flag for ending the event
        self.event_ended = False
    
    def trigger(self) -> str:
        """
        Trigger and execute the event.
        
        This method should implement the event's main logic,
        building and executing actions as needed.
        
        Returns:
            Execution result: None/"DEATH"/"WIN"
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement trigger()")
    
    def execute_actions(self) -> str:
        """
        Execute all actions in the event's action queue.
        
        This is a helper method for events to execute their actions.
        Stops executing when event_ended is True or queue is empty.
        
        Returns:
            Execution result if special value encountered, None otherwise
        """
        while not self.event_ended and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            
            # Check for special return values
            if result in ("DEATH", "WIN"):
                return result
        
        return None
    
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
    
    def trigger(self) -> str:
        """Trigger combat event"""
        from engine.combat import Combat
        from actions.display import DisplayTextAction
        
        # Display event description
        self.action_queue.add_action(DisplayTextAction(
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
        
        return result
    
    def _handle_victory(self):
        """Handle combat victory - add event-specific rewards"""
        # Subclasses can override to add custom rewards
        pass