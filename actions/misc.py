"""
Miscellaneous actions (room, shop, treasure).
"""
import random
from typing import Optional
from actions.base import Action, LambdaAction
from actions.card import AddCardAction
from actions.display import InputRequestAction
from actions.reward import AddRelicAction, AddGoldAction, AddRandomPotionAction, AddRelicByNameAction
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
        gold_spent = 0
        from engine.game_state import game_state
        from actions.card import ChooseRemoveCardAction
        from tui.print_utils import tui_print
        from localization import t
        from utils.result_types import BaseResult

        if not game_state:
            return NoneResult()

        player = getattr(game_state, "player", None)
        player_gold = getattr(player, "gold", 0)
        if not isinstance(player_gold, (int, float)):
            player_gold = 0

        if self.shop_item.item_type == "card_removal":
            final_price = getattr(self.shop_item, "base_price", 0)
            assert player_gold >= final_price
            gold_spent = final_price
            game_state.player.gold -= final_price

            if hasattr(game_state, 'current_room') and hasattr(game_state.current_room, 'card_removal_used'):
                game_state.current_room.card_removal_used = True
                if not _has_relic("SmilingMask", game_state):
                    if hasattr(game_state.current_room, 'card_removal_price'):
                        game_state.current_room.card_removal_price += 25

            tui_print(t("ui.shop_removed_card", default="Removed a card from deck"))

            if _has_relic("MawBank", game_state):
                game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent

            actions = []
            remove_result = ChooseRemoveCardAction(pile='deck').execute()
            if isinstance(remove_result, SingleActionResult):
                actions.append(remove_result.action)
            elif isinstance(remove_result, MultipleActionsResult):
                actions.extend(remove_result.actions)
            follow_up = self._build_follow_up_menu(game_state)
            if follow_up:
                actions.append(follow_up)
            return MultipleActionsResult(actions) if actions else NoneResult()

        ascension = getattr(game_state, "ascension_level", 0) if game_state else 0
        if not isinstance(ascension, (int, float)):
            ascension = 0
        final_price = self.shop_item.get_final_price_with_modifiers(ascension, game_state)

        assert player_gold >= final_price
        gold_spent = final_price
        game_state.player.gold -= final_price

        actions = []
        if self.shop_item.item_type == "card":
            add_result = AddCardAction(card=self.shop_item.item, dest_pile="deck", source="shop").execute()
            if isinstance(add_result, SingleActionResult):
                actions.append(add_result.action)
            elif isinstance(add_result, MultipleActionsResult):
                actions.extend(add_result.actions)
        elif self.shop_item.item_type == "relic":
            relic_result = AddRelicByNameAction(relic_id=self.shop_item.item.idstr).execute()
            if isinstance(relic_result, SingleActionResult):
                actions.append(relic_result.action)
            elif isinstance(relic_result, MultipleActionsResult):
                actions.extend(relic_result.actions)
        elif self.shop_item.item_type == "potion":
            potion_result = AddRandomPotionAction(character=game_state.player.character).execute()
            if isinstance(potion_result, SingleActionResult):
                actions.append(potion_result.action)
            elif isinstance(potion_result, MultipleActionsResult):
                actions.extend(potion_result.actions)

        self.shop_item.purchased = True

        if _has_relic("TheCourier", game_state):
            should_restock = True
            for relic in game_state.player.relics:
                hook = getattr(relic, "should_restock_shop_item", None)
                if hook:
                    should_restock = hook(self.shop_item.item_type, self.shop_item.item)
                    break
            if should_restock:
                self._restock_shop_item(game_state)

        item_name = getattr(self.shop_item.item, 'display_name', None)
        if item_name is not None:
            item_name = str(item_name)
        else:
            item_name = getattr(self.shop_item.item, 'name', 'Unknown Item')
        tui_print(t("ui.shop_bought_item", default=f"Bought {item_name} for {final_price} gold!"))

        if _has_relic("MawBank", game_state):
            game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent

        follow_up = self._build_follow_up_menu(game_state)
        if follow_up:
            actions.append(follow_up)
        return MultipleActionsResult(actions) if actions else NoneResult()

    def _build_follow_up_menu(self, game_state):
        room = getattr(game_state, "current_room", None)
        if room is None or getattr(room, "should_leave", False):
            return None
        build_menu = getattr(room, "_build_shop_menu", None)
        if build_menu is None:
            return None
        return build_menu()

    def _restock_shop_item(self, game_state) -> None:
        """Replace purchased shop slot with a new generated item."""
        from rooms.shop_state import restock_shop_item

        player = getattr(game_state, "player", None)
        if not player:
            return

        restock_shop_item(self.shop_item, player)


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
                    actions=[AddRelicByNameAction(relic_id=relic.idstr)]
                ))

            options.append(Option(
                name=LocalStr("ui.skip_relic"),
                actions=[]
            ))

            select_action = InputRequestAction(
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
                actions.append(AddRelicByNameAction(relic_id=relic.idstr))
                
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
                actions.append(AddRelicByNameAction(relic_id=relic.idstr))
                
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
                actions.append(AddRelicByNameAction(relic_id=relic.idstr))
                
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

@register("action")
class BottledCardInputRequestAction(Action):
    """Select a card from deck to bottle with a relic.
    
    Required:
        relic (Relic): The relic that will store the selected card
        card_type (CardType): Type of card to select (ATTACK, SKILL, or POWER)
    """
    
    def __init__(self, relic, card_type):
        self.relic = relic
        self.card_type = card_type
    
    def execute(self):
        from engine.game_state import game_state
        from actions.display import InputRequestAction
        from utils.option import Option
        from utils.result_types import SingleActionResult
        from utils.random import get_random_card
        from localization import LocalStr
        
        # Get all cards from deck
        card_manager = game_state.player.card_manager
        deck = card_manager.get_pile('deck')
        
        # Filter by card type
        cards_to_choose = []
        for card in deck:
            if hasattr(card, 'card_type') and card.card_type == self.card_type:
                cards_to_choose.append(card)
        
        # Show random cards of chosen type as options
        # This matches original game behavior where you choose from a pool
        namespace = game_state.player.namespace if game_state.player else None
        
        options = []
        selected_card_ids = []
        for _ in range(3):
            random_card = get_random_card(
                namespaces=[namespace] if namespace else None,
                card_types=[self.card_type],
                exclude_card_ids=selected_card_ids
            )
            if random_card:
                selected_card_ids.append(random_card.idstr)
                # Create a LambdaAction that will set the card when executed
                set_card_action = LambdaAction(
                    func=lambda c=random_card: setattr(self.relic, 'selected_card', c)
                )
                options.append(
                    Option(
                        name=random_card.display_name,
                        actions=[set_card_action]
                    )
                )
        
        if not options:
            print(f"No cards of type {self.card_type} available")
            from utils.result_types import NoneResult
            return NoneResult()
        
        select_action = InputRequestAction(
            title=LocalStr("ui.choose_card_to_bottle", default="Choose a card to bottle"),
            options=options,
            max_select=1,
            must_select=True
        )
        return SingleActionResult(select_action)
