"""
Miscellaneous actions (room, shop, treasure).
"""
import random
from typing import Optional
from actions.base import Action
from actions.card import AddCardAction
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddGoldAction, AddRandomPotionAction
from utils.result_types import BaseResult, GameStateResult, MultipleActionsResult, NoneResult, SingleActionResult
from localization import LocalStr, t
from utils.option import Option
from utils.random import get_random_relic
from utils.registry import register
from utils.types import RarityType
from tui.print_utils import tui_print


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
        room: The room to leave (optional, uses current_room if not specified)
    """
    def __init__(self, room=None):
        self.room = room

    def execute(self) -> 'BaseResult':
        """Leave a room and return to map state"""
        from engine.game_state import game_state

        # Mark room should leave flag
        target_room = self.room if self.room else game_state.current_room
        if target_room:
            target_room.should_leave = True

        return NoneResult()
    
@register("action")
class EscapeAction(Action):
    """Escape from combat and return to map state

    Required:
        None

    Optional:
        None
    """
    def __init__(self):
        pass

    def execute(self) -> 'BaseResult':
        """Escape from combat and return to map state"""
        return GameStateResult(state="COMBAT_ESCAPE")

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
            AddCardAction(card=self.shop_item.item, dest_pile="discard", source="shop").execute()
        elif self.shop_item.item_type == "relic":
            AddRelicAction(relic=self.shop_item.item.idstr).execute()
        elif self.shop_item.item_type == "potion":
            AddRandomPotionAction(character=game_state.player.character).execute()

        self.shop_item.purchased = True

        # TheCourier: restock cards/relics/potions after purchase.
        if _has_relic("TheCourier", game_state):
            should_restock = True
            for relic in game_state.player.relics:
                hook = getattr(relic, "should_restock_shop_item", None)
                if hook:
                    should_restock = hook(self.shop_item.item_type, self.shop_item.item)
                    break
            if should_restock:
                self._restock_shop_item(game_state)

        # Get item name - cards use display_name, relics use name
        item_name = getattr(self.shop_item.item, 'display_name', None)
        if item_name is not None:
            item_name = str(item_name)  # BaseLocalStr to string
        else:
            item_name = getattr(self.shop_item.item, 'name', 'Unknown Item')
        tui_print(t("ui.shop_bought_item", default=f"Bought {item_name} for {final_price} gold!"))

        # feature: MawBank的逻辑
        # MawBank effect: track gold spent
        if _has_relic("MawBank", game_state):
            game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent
        return NoneResult()

    def _restock_shop_item(self, game_state) -> None:
        """Replace purchased shop slot with a new generated item."""
        from rooms.shop import ShopItem
        from utils.random import get_random_card, get_random_relic, get_random_potion
        from utils.types import RarityType, CardType
        import random

        player = game_state.player
        if not player:
            return

        namespace = player.namespace
        if any(getattr(r, "idstr", None) == "PrismaticShard" for r in player.relics):
            card_namespaces = None
        else:
            card_namespaces = [namespace]

        if self.shop_item.item_type == "card":
            card_type = random.choice([CardType.ATTACK, CardType.SKILL, CardType.POWER])
            new_item = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[card_type],
                namespaces=card_namespaces,
            )
            if not new_item:
                return
            if new_item.rarity == RarityType.COMMON:
                base_price = random.randint(45, 55)
            elif new_item.rarity == RarityType.UNCOMMON:
                base_price = random.randint(68, 83)
            else:
                base_price = random.randint(135, 165)
            self.shop_item.item = new_item
            self.shop_item.base_price = base_price
            self.shop_item.discount = 0
            self.shop_item.purchased = False
            return

        if self.shop_item.item_type == "potion":
            rarity_roll = random.random()
            rarity = (
                RarityType.COMMON
                if rarity_roll < 0.65
                else RarityType.UNCOMMON if rarity_roll < 0.90 else RarityType.RARE
            )
            new_item = get_random_potion(rarities=[rarity])
            if not new_item:
                return
            if rarity == RarityType.COMMON:
                base_price = random.randint(48, 53)
            elif rarity == RarityType.UNCOMMON:
                base_price = random.randint(71, 79)
            else:
                base_price = random.randint(95, 105)
            self.shop_item.item = new_item
            self.shop_item.base_price = base_price
            self.shop_item.discount = 0
            self.shop_item.purchased = False
            return

        if self.shop_item.item_type == "relic":
            rarity_roll = random.random()
            rarity = (
                RarityType.COMMON
                if rarity_roll < 0.50
                else RarityType.UNCOMMON if rarity_roll < 0.83 else RarityType.RARE
            )
            new_item = get_random_relic(rarities=[rarity])
            if not new_item:
                return
            if rarity == RarityType.COMMON:
                base_price = random.randint(143, 158)
            elif rarity == RarityType.UNCOMMON:
                base_price = random.randint(238, 263)
            else:
                base_price = random.randint(285, 315)
            self.shop_item.item = new_item
            self.shop_item.base_price = base_price
            self.shop_item.discount = 0
            self.shop_item.purchased = False


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
        chest_open_actions = self.treasure_room.get_chest_open_actions()
        empty_chest = False

        if game_state and game_state.player:
            for relic in list(game_state.player.relics):
                hook = getattr(relic, "should_empty_chest", None)
                if not hook:
                    continue
                if hook(chest_type=self.treasure_room.chest_type):
                    empty_chest = True
                    break

        if empty_chest:
            return MultipleActionsResult(chest_open_actions)

        # Handle chest contents based on type
        if self.treasure_room.chest_type == "boss":
            # 3 boss relics to choose from
            relics = []
            for _ in range(3):
                relic = get_random_relic(rarities=[RarityType.BOSS])
                if relic:
                    relics.append(relic)

            assert len(relics) == 3, "cannot get random relics"

            # Create selection options
            options = []
            for relic in relics:
                options.append(Option(
                    name=LocalStr("ui.choose_relic", name=relic.local("name")),
                    actions=[AddRelicAction(relic=relic.idstr)]
                ))

            options.append(Option(
                name=LocalStr("ui.skip_relic"),
                actions=[]
            ))

            select_action = SelectAction(
                title=LocalStr("ui.choose_boss_relic"),
                options=options
            )
            if chest_open_actions:
                return MultipleActionsResult(chest_open_actions + [select_action])
            return SingleActionResult(select_action)

        elif self.treasure_room.chest_type == "small":
            actions = []
            if random.random() < 0.50:
                gold = random.randint(23, 27)
                actions.append(AddGoldAction(amount=gold))
            if random.random() < 0.75:
                rarities = [RarityType.COMMON]
            else:
                rarities = [RarityType.UNCOMMON]
            relic = get_random_relic(rarities=rarities)
            if relic:
                actions.append(AddRelicAction(relic=relic.idstr))
                
            return MultipleActionsResult(chest_open_actions + actions)
            
        elif self.treasure_room.chest_type == "medium":
            actions = []
            if random.random() < 0.35:
                gold = random.randint(45, 55)
                actions.append(AddGoldAction(amount=gold))
            relic_random = random.random()
            if relic_random < 0.35:
                rarities = [RarityType.COMMON]
            elif relic_random < 0.85:
                rarities = [RarityType.UNCOMMON]
            else:
                rarities = [RarityType.RARE]
            relic = get_random_relic(rarities=rarities)
            if relic:
                actions.append(AddRelicAction(relic=relic.idstr))
                
            return MultipleActionsResult(chest_open_actions + actions)

        elif self.treasure_room.chest_type == "large":
            actions = []
            if random.random() < 0.50:
                gold = random.randint(68, 82)
                actions.append(AddGoldAction(amount=gold))
            if random.random() < 0.75:
                rarities = [RarityType.UNCOMMON]
            else:
                rarities = [RarityType.RARE]
            relic = get_random_relic(rarities=rarities)
            if relic:
                actions.append(AddRelicAction(relic=relic.idstr))
                
            return MultipleActionsResult(chest_open_actions + actions)
        
        else:
            raise ValueError(f"Invalid chest type: {self.treasure_room.chest_type}")


@register("action")
class SkipToBossAction(Action):
    """Skip to the boss floor.
    
    Required:
        None
        
    Optional:
        None
    """
    def execute(self) -> 'BaseResult':
        """Skip to boss floor."""
        from engine.game_state import game_state
        
        # Set flag to skip to boss
        game_state.skip_to_boss = True
        tui_print("[Event] Skipping to boss!")
        return NoneResult()
