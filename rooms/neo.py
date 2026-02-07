"""
Neo reward room - starting room where player chooses their blessing.
"""
from actions.display import DisplayTextAction
from utils.result_types import GameStateResult, NoneResult
from rooms.base import Room, BaseResult
from utils.registry import register


@register("room")
class NeoRewardRoom(Room):
    """Neo reward blessing room - the starting room"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = None  # Special room, doesn't have standard type
    
    def init(self):
        """Initialize Neo room - no special initialization needed"""
    
    def enter(self) -> BaseResult:
        """Enter Neo room and trigger blessing selection"""
        from engine.game_state import game_state

        # Display welcome message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="ui.neo_welcome",
            default="Welcome, traveler. I am Neow. I shall grant you a blessing to begin your journey."
        ))

        # Create and trigger Neo event
        from events.neo_event import NeoEvent
        neo_event = NeoEvent()

        # Execute Neo event
        result = neo_event.trigger()
        
        if isinstance(result, GameStateResult):
            return result
        
        # Display goodbye message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="ui.neo_goodbye",
            default="Your journey begins now. Good luck!"
        ))
        
        # Neo room is done, player should leave
        self.should_leave = True
        
        # Execute any remaining actions
        return game_state.execute_all_actions()