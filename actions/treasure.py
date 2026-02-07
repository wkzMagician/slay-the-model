"""
Treasure room-related actions.
"""
import random
from typing import Optional
from actions.base import Action
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddGoldAction
from utils.result_types import BaseResult, NoneResult, SingleActionResult
from localization import LocalStr, t
from utils.option import Option
from utils.random import get_random_relic
from utils.registry import register
from utils.types import RarityType


@register("action")
class OpenChestAction(Action):
    """Action to open a treasure chest"""

    def __init__(self, treasure_room):
        self.treasure_room = treasure_room

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.treasure_room.chest_opened:
            return NoneResult()

        self.treasure_room.chest_opened = True

        # Handle chest contents based on type
        if self.treasure_room.chest_type == "boss":
            # 3 boss relics to choose from
            relics = []
            for _ in range(3):
                relics.append(get_random_relic(rarities=[RarityType.BOSS]))

            # Create selection options
            options = []
            for relic in relics:
                options.append(Option(
                    name=LocalStr("ui.choose_relic", name=relic.name),
                    actions=[AddRelicAction(relic=relic.idstr)]
                ))

            options.append(Option(
                name=LocalStr("ui.skip_relic"),
                actions=[]
            ))

            # Return SelectAction to be added to room's action_queue
            return SingleActionResult(SelectAction(
                title=LocalStr("ui.choose_boss_relic"),
                options=options
            ))

        elif self.treasure_room.chest_type == "small":
            roll = random.random()
            if roll < 0.50:
                gold = random.randint(23, 27)
                AddGoldAction(amount=gold).execute()
                print(t("ui.found_gold", default=f"Found {gold} gold!"))
            else:
                rarity = RarityType.COMMON if random.random() < 0.75 else RarityType.UNCOMMON
                relic = get_random_relic(rarities=[rarity])
                if relic is None:
                    print(f"Failed to get a random relic with rarity {rarity.value}")
                else:
                    AddRelicAction(relic=relic.idstr).execute()
                    print(t("ui.found_relic", default=f"Found {relic.idstr}!"))
            return NoneResult()

        elif self.treasure_room.chest_type == "medium":
            roll = random.random()
            if roll < 0.35:
                gold = random.randint(45, 55)
                AddGoldAction(amount=gold).execute()
                print(t("ui.found_gold", default=f"Found {gold} gold!"))
            else:
                roll = random.random()
                rarity = RarityType.COMMON if roll < 0.35 else RarityType.UNCOMMON if roll < 0.85 else RarityType.RARE
                relic = get_random_relic(rarities=[rarity])
                if relic is None:
                    print(f"Failed to get a random relic with rarity {rarity.value}")
                else:
                    AddRelicAction(relic=relic.idstr).execute()
                    print(t("ui.found_relic", default=f"Found {relic.idstr}!"))
            return NoneResult()

        elif self.treasure_room.chest_type == "large":
            roll = random.random()
            if roll < 0.50:
                gold = random.randint(68, 82)
                AddGoldAction(amount=gold).execute()
                print(t("ui.found_gold", default=f"Found {gold} gold!"))
            else:
                rarity = RarityType.UNCOMMON if random.random() < 0.75 else RarityType.RARE
                relic = get_random_relic(rarities=[rarity])
                if relic is None:
                    print(f"Failed to get a random relic with rarity {rarity.value}")
                else:
                    AddRelicAction(relic=relic.idstr).execute()
                    print(t("ui.found_relic", default=f"Found {relic.idstr}!"))
            return NoneResult()
        
        else:
            raise ValueError(f"Invalid chest type: {self.treasure_room.chest_type}")