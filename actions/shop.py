"""
Shop-related actions.
"""
from actions.base import Action
from actions.card import AddCardAction
from actions.display import SelectAction
from actions.reward import AddRelicAction, AddRandomPotionAction
from engine.game_state import game_state
from localization import LocalStr, t
from utils.registry import register


@register("action")
class BuyItemAction(Action):
    """Action to buy an item from shop"""

    def __init__(self, shop_item, item_idx):
        self.shop_item = shop_item
        self.item_idx = item_idx

    def execute(self):
        ascension = game_state.ascension_level if game_state else 0
        final_price = _get_final_price(self.shop_item, ascension)

        if game_state.player.gold >= final_price:
            game_state.player.gold -= final_price

            if self.shop_item.item_type == "card":
                AddCardAction(card=self.shop_item.item).execute()
            elif self.shop_item.item_type == "relic":
                AddRelicAction(relic=self.shop_item.item.idstr).execute()
            elif self.shop_item.item_type == "potion":
                AddRandomPotionAction(character=game_state.player.character).execute()

            self.shop_item.purchased = True

            if self.shop_item.item_type != "relic" and _has_relic("TheCourier"):
                # TODO: Implement restock logic
                pass
            
            print(t("ui.shop_bought_item", default=f"Bought {self.shop_item.item.name} for {final_price} gold!"))
            game_state.current_room.enter()
        else:
            print(t("ui.not_enough_gold", default="Not enough gold!"))


@register("action")
class CardRemovalAction(Action):
    """Action to remove a card using shop service"""

    def __init__(self, shop_room):
        self.shop_room = shop_room

    def execute(self):
        price = self.shop_room.card_removal_price
        if _has_relic("SmilingMask"):
            price = 50
        elif _has_relic("MembershipCard"):
            price = int(price * 0.5)

        if game_state.player.gold >= price:
            game_state.player.gold -= price
            self.shop_room.card_removal_used = True

            if not _has_relic("SmilingMask"):
                self.shop_room.card_removal_price += 25

            print(t("ui.card_removal_complete", default="Card removal complete!"))
            game_state.current_room.enter()
        else:
            print(t("ui.not_enough_gold", default="Not enough gold!"))


@register("action")
class LeaveShopAction(Action):
    """Action to leave of shop"""

    def execute(self):
        if _has_relic("MawBank"):
            # TODO: Track gold spending
            pass
        game_state.current_room.leave()


def _has_relic(relic_name: str) -> bool:
    """Check if player has a specific relic"""
    for relic in game_state.player.relics:
        if relic.idstr == relic_name:
            return True
    return False


def _get_final_price(shop_item, ascension_level):
    """Calculate final price with all modifiers"""
    final_price = shop_item.get_final_price(ascension_level)

    if _has_relic("MembershipCard"):
        final_price = int(final_price * 0.5)

    if _has_relic("TheCourier") and shop_item.purchased:
        final_price = int(final_price * 0.8)

    if shop_item.item_type == "remove" and _has_relic("SmilingMask"):
        final_price = 50

    return final_price