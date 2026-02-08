"""
Miscellaneous actions (room, shop, treasure).
"""
import random
from typing import Optional
from actions.base import Action
from actions.card import AddCardAction
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddGoldAction, AddRandomPotionAction
from utils.result_types import BaseResult, NoneResult, SingleActionResult
from localization import LocalStr, t
from utils.option import Option
from utils.random import get_random_relic
from utils.registry import register
from utils.types import RarityType


# ============================================================================
# Helper Functions
# ============================================================================

def _has_relic(relic_key: str, game_state=None) -> bool:
    """Check if player has a specific relic"""
    if not game_state:
        return False
    if not game_state.player:
        return False

    target = relic_key.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    for relic in game_state.player.relics:
        relic_id = getattr(relic, "idstr", None)
        if relic_id and relic_id.strip().lower().replace(" ", "").replace("_", "").replace("-", "") == target:
            return True
        relic_name = getattr(relic, "name", None)
        if relic_name and relic_name.strip().lower().replace(" ", "").replace("_", "").replace("-", "") == target:
            return True

    return False


# ============================================================================
# Room Actions
# ============================================================================

@register("action")
class LeaveRoomAction(Action):
    """Leave a room and return to map state

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Leave a room and return to map state"""
        from engine.game_state import game_state

        # Mark room should leave flag
        if game_state.current_room:
            game_state.current_room.should_leave = True

        return NoneResult()


# ============================================================================
# Shop Actions
# ============================================================================

@register("action")
class BuyItemAction(Action):
    """Action to buy an item from shop"""

    def __init__(self, shop_item, item_idx):
        self.shop_item = shop_item
        self.item_idx = item_idx

    def execute(self) -> 'BaseResult':
        # Track gold spent for MawBank relic
        gold_spent = 0
        from engine.game_state import game_state
        if not game_state:
            return NoneResult()

        ascension = getattr(game_state, "ascension_level", 0) if game_state else 0
        final_price = self.shop_item.get_final_price_with_modifiers(ascension, game_state)

        assert game_state.player.gold >= final_price
        gold_spent = final_price
        game_state.player.gold -= final_price

        if self.shop_item.item_type == "card":
            AddCardAction(card=self.shop_item.item).execute()
        elif self.shop_item.item_type == "relic":
            AddRelicAction(relic=self.shop_item.item.idstr).execute()
        elif self.shop_item.item_type == "potion":
            AddRandomPotionAction(character=game_state.player.character).execute()

        self.shop_item.purchased = True

        if self.shop_item.item_type != "relic" and _has_relic("TheCourier", game_state):
            # TheCourier restock: when relic items are bought, restock at 80% price
            self.shop_item.price_multiplier = 0.8

        print(t("ui.shop_bought_item", default=f"Bought {self.shop_item.item.name} for {final_price} gold!"))

        # todo: MawBank的逻辑
        # MawBank effect: track gold spent
        if _has_relic("MawBank", game_state):
            game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent
        return NoneResult()


# ============================================================================
# Treasure Actions
# ============================================================================

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