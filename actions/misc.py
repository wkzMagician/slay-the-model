"""
Miscellaneous actions
"""
from actions.base import Action
from localization import t
from utils.registry import register


@register("action")
class MoveToMapNodeAction(Action):
    """Move to a specific map node
    
    Required:
        floor (int): Target floor number
        position (int): Target position on that floor
        
    Optional:
        None
    """
    def __init__(self, floor: int, position: int):
        self.floor = floor
        self.position = position
    
    def execute(self):
        from engine.game_state import game_state
        
        # Get map manager
        map_manager = game_state.map_manager
        if not map_manager:
            print("Error: Map not initialized")
            return
        
        # Move to the specified node
        new_room = map_manager.move_to_node(self.floor, self.position)
        
        # Update game state
        game_state.current_room = new_room
        
        # Enter the new room
        new_room.enter_room()
        
        # Set game phase to room
        game_state.game_phase = "room"

@register("action")
class GenerateMapAction(Action):
    """Generate a new map and update global state
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        game_state.generate_initial_map()
        print(self.translate("ui.map_generated", default="Map generated for new act!"))

@register("action")
class StartEventAction(Action):
    """Action to start an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.start_event()
            
@register("action")
class EndEventAction(Action):
    """Action to end an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.end_event()