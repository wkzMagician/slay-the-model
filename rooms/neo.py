"""
Neo reward room - the starting room where player chooses their blessing.
"""
from actions.display import DisplayTextAction
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room
from utils.registry import register


@register("room")
class NeoRewardRoom(Room):
    """Neo reward blessing room - the starting room"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = None  # Special room, doesn't have standard type
    
    def init(self):
        """Initialize Neo room - no special initialization needed"""
        pass
    
    def enter(self) -> str:
        """Enter Neo room and trigger blessing selection"""
        # Display welcome message
        self.action_queue.add_action(DisplayTextAction(
            text_key="ui.neo_welcome",
            default="Welcome, traveler. I am Neow. I shall grant you a blessing to begin your journey."
        ))
        
        # Create and trigger Neo event
        from events.neo_event import NeoEvent
        neo_event = NeoEvent()
        
        # Execute the Neo event
        result = neo_event.trigger()
        
        # Check for game end
        if result in ("DEATH", "WIN"):
            return result
        
        # Display goodbye message
        self.action_queue.add_action(DisplayTextAction(
            text_key="ui.neo_goodbye",
            default="Your journey begins now. Good luck!"
        ))
        
        # Neo room is done, player should leave
        self.should_leave = True
        
        # Execute any remaining actions
        return self.execute_actions()