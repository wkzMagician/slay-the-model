"""
Treasure room implementation.
"""
import random
from actions.display import SelectAction, DisplayTextAction
from actions.treasure import OpenChestAction
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room
from utils.option import Option
from utils.registry import register
from utils.types import RoomType


@register("room")
class TreasureRoom(Room):
    """Treasure room where player can open chests"""

    def __init__(self, is_boss=False, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.TREASURE
        self.localization_prefix = "rooms"
        self.is_boss = is_boss
        self.chest_type = None
        self.chest_opened = False
    
    def init(self):
        """Initialize the treasure room"""
        # Determine chest type
        if self.is_boss:
            self.chest_type = "boss"
        else:
            roll = random.random()
            self.chest_type = "small" if roll < 0.50 else "medium" if roll < 0.83 else "large"
    
    def enter(self) -> str:
        """Enter treasure room and handle chest opening"""
        # Display entry message
        self.action_queue.add_action(DisplayTextAction(
            text_key="rooms.treasure.enter"
        ))
        
        # Main treasure loop
        while not self.should_leave:
            # Build treasure menu
            self._build_treasure_menu()
            
            # Execute actions
            result = self.execute_actions()
            
            # Check for game end
            if result in ("DEATH", "WIN"):
                return result
            
            # Rebuild menu if not leaving and chest not opened
            if not self.should_leave and not self.chest_opened:
                self.action_queue.clear()
        
        return None
    
    def _build_treasure_menu(self):
        """Build the treasure room menu"""
        options = []
        
        # Open chest option
        if not self.chest_opened:
            if self.is_boss:
                name = self.local("TreasureRoom.open_boss_chest")
            else:
                name = self.local("TreasureRoom.open_chest", chest_type=self.chest_type)
            options.append(Option(
                name=name,
                actions=[OpenChestAction(self)]
            ))
        else:
            # Chest already opened, just leave
            options.append(Option(
                name=self.local("TreasureRoom.leave"),
                actions=[LeaveTreasureAction()]
            ))
        
        # Add selection action to queue
        self.action_queue.add_action(SelectAction(
            title=self.local("TreasureRoom.boss_title") if self.is_boss else self.local("TreasureRoom.title"),
            options=options
        ))
    
    def execute_actions(self) -> str:
        """Execute actions from queue, handle special return values"""
        while not self.should_leave and not self.action_queue.is_empty():
            result = self.action_queue.execute_next()
            
            # Check if OpenChestAction returned a SelectAction (for boss chest)
            if result and isinstance(result, SelectAction):
                self.action_queue.add_action(result)
            
            # Check for game end
            if result in ("DEATH", "WIN"):
                return result
        
        return None


class LeaveTreasureAction:
    """Action to leave the treasure room"""
    
    def execute(self):
        """Set should_leave flag on current room"""
        room = game_state.current_room
        if isinstance(room, TreasureRoom):
            room.should_leave = True
        return None