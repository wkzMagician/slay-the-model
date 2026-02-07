"""
Shop-related actions.
"""
from typing import Optional
from actions.base import Action
from actions.card import AddCardAction
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddRandomPotionAction
from utils.result_types import BaseResult, NoneResult
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register


# Import shop helper functions from rooms module
# This consolidates relic checking logic in one place
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
        game_state.current_room.enter()

        # todo: MawBank的逻辑
        # MawBank effect: track gold spent
        if _has_relic("MawBank", game_state):
            game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent
        return NoneResult()