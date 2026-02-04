"""
Room-related actions.
"""
from actions.base import Action
from utils.registry import register


@register("action")
class TriggerRelicAction(Action):
    """Trigger a relic's passive or active effect
    
    Required:
        relic_name (str): Name of the relic to trigger
        
    Optional:
        None
    """
    def __init__(self, relic_name: str):
        self.relic_name = relic_name
    
    def execute(self):
        """Trigger the relic's effect"""
        from engine.game_state import game_state
        if not game_state.player:
            return
        
        # Find the relic
        from utils.registry import get_registered
        relic = get_registered("relic", self.relic_name)
        if not relic:
            return
        
        # Trigger the relic's effect (call on_trigger or similar)
        # Relics implement their own trigger logic
        if hasattr(relic, "on_trigger"):
            relic.on_trigger()
        elif hasattr(relic, "passive"):
            relic.passive()


@register("action")
class LeaveRoomAction(Action):
    """Action to leave a room and return to map state"""
    
    def __init__(self, room):
        self.room = room
    
    def execute(self):
        """Leave the room and mark room as completed"""
        from engine.game_state import game_state
        # Mark room should leave flag
        self.room.should_leave = True
