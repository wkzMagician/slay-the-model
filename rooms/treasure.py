"""
Treasure room implementation.
"""
import random
from tui.print_utils import tui_print
from actions.display import InputRequestAction, DisplayTextAction
from actions.misc import OpenChestAction
from utils.result_types import GameStateResult, NoneResult, MultipleActionsResult, SingleActionResult
from engine.game_state import game_state
from localization import LocalStr, t
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
        self._determine_chest_type()

    def _determine_chest_type(self):
        """Determine type of chest based on random roll. Returns a chest type string."""
        if self.is_boss:
            self.chest_type = "boss"
        else:
            roll = random.random()
            self.chest_type = "small" if roll < 0.50 else "medium" if roll < 0.83 else "large"
        return self.chest_type

    def _get_small_chest_contents(self):
        """Get contents for a small chest."""
        import random
        from utils.types import RarityType
        from relics.relics import get_random_relic_by_rarity
        # Small chest: 23-27 gold + 1 common relic
        gold = random.randint(23, 27)
        relic_classes = get_random_relic_by_rarity(RarityType.COMMON)
        relic = relic_classes[0]() if relic_classes else None
        return {"gold": gold, "relic": RarityType.COMMON, "relics": [relic] if relic else []}

    def _get_medium_chest_contents(self):
        """Get contents for a medium chest."""
        import random
        from utils.types import RarityType
        from relics.relics import get_random_relic_by_rarity
        # Medium chest: 45-55 gold + 1 uncommon relic
        gold = random.randint(45, 55)
        relic_classes = get_random_relic_by_rarity(RarityType.UNCOMMON)
        relic = relic_classes[0]() if relic_classes else None
        return {"gold": gold, "relic": RarityType.UNCOMMON, "relics": [relic] if relic else []}

    def _get_large_chest_contents(self):
        """Get contents for a large chest."""
        import random
        from utils.types import RarityType
        from relics.relics import get_random_relic_by_rarity
        # Large chest: 68-82 gold + 1 rare relic
        gold = random.randint(68, 82)
        relic_classes = get_random_relic_by_rarity(RarityType.RARE)
        relic = relic_classes[0]() if relic_classes else None
        return {"gold": gold, "relic": RarityType.RARE, "relics": [relic] if relic else []}

    def _get_boss_chest_contents(self):
        """Get contents for a boss chest."""
        from utils.types import RarityType
        from relics.relics import get_random_relic_by_rarity
        # Boss chest: choice of boss relics
        boss_relic_classes = get_random_relic_by_rarity(RarityType.BOSS, count=3)
        boss_relics = [cls() for cls in boss_relic_classes]
        return {"gold": 0, "relic": RarityType.BOSS, "relics": boss_relics}

    def get_chest_open_actions(self):
        """Collect relic actions triggered when this chest is opened."""
        if not game_state or not game_state.player:
            return []

        actions = []
        for relic in list(game_state.player.relics):
            hook = getattr(relic, "on_chest_open", None)
            if not hook:
                continue
            result = hook(chest_type=self.chest_type)
            if not result:
                continue
            if isinstance(result, list):
                actions.extend(result)
            else:
                actions.append(result)
        return actions

    def enter(self) -> BaseResult:
        """Enter treasure room and return the initial treasure actions."""
        return MultipleActionsResult([
            DisplayTextAction(text_key="rooms.TreasureRoom.enter"),
            self._build_treasure_menu(),
        ])

    def _build_treasure_menu(self):
        """Build treasure room menu and return InputRequestAction"""
        options = []

        # Open chest option
        if not self.chest_opened:
            if self.is_boss:
                name = self.local("open_boss_chest")
            else:
                name = self.local("open_chest", chest_type=self.chest_type)
            options.append(Option(
                name=name,
                actions=[OpenChestAction(self)]
            ))
        else:
            # Chest already opened, just leave
            options.append(Option(
                name=self.local("leave"),
                actions=[]
            ))

        # Create InputRequestAction and add to action queue
        select_action = InputRequestAction(
            title=self.local("boss_title") if self.is_boss else self.local("title"),
            options=options
        )
        self.action_queue.add_action(select_action)
        return select_action
