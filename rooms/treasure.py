"""
Treasure room implementation.
"""
import random
from actions.display import SelectAction, DisplayTextAction
from actions.misc import OpenChestAction
from utils.result_types import GameStateResult, NoneResult, MultipleActionsResult
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
        entry_action = DisplayTextAction(text_key="rooms.treasure.enter")

        # Main treasure loop
        while not self.should_leave:
            # Build treasure menu
            select_action = self._build_treasure_menu()

            if select_action:
                # Return entry message on first iteration, then select action
                if entry_action:
                    actions = [entry_action, select_action]
                    entry_action = None  # Only show entry message once
                else:
                    actions = [select_action]

                return MultipleActionsResult(actions)
            else:
                # No actions to return, break loop
                break

        return NoneResult()
    
    def _build_treasure_menu(self):
        """Build treasure room menu and return SelectAction"""
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

        # Return SelectAction instead of adding to queue
        return SelectAction(
            title=self.local("TreasureRoom.boss_title") if self.is_boss else self.local("TreasureRoom.title"),
            options=options
        )