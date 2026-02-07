"""
Treasure room implementation.
"""
import random
from actions.display import SelectAction, DisplayTextAction
from actions.treasure import OpenChestAction
from utils.result_types import GameStateResult, NoneResult
from engine.game_state import game_state
from localization import LocalStr
from rooms.base import Room, BaseResult
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
    
    def enter(self) -> BaseResult:
        """Enter treasure room and handle chest opening"""
        # Display entry message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="rooms.treasure.enter"
        ))

        # Main treasure loop
        while not self.should_leave:
            # Build treasure menu
            self._build_treasure_menu()

            # Execute actions
            result = game_state.execute_all_actions()

            if isinstance(result, GameStateResult):
                return result

            # Rebuild menu if not leaving and chest not opened
            if not self.should_leave and not self.chest_opened:
                game_state.action_queue.clear()

        return NoneResult()
    
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
                actions=[]
            ))
        
        # Add selection action to global queue
        game_state.action_queue.add_action(SelectAction(
            title=self.local("TreasureRoom.boss_title") if self.is_boss else self.local("TreasureRoom.title"),
            options=options
        ))