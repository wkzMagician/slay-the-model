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
        # Track gold spent for MawBank relic
        gold_spent = 0
        from engine.game_state import game_state
        if not game_state:
            return

        ascension = getattr(game_state, "ascension_level", 0) if game_state else 0
        final_price = _get_final_price(self.shop_item, ascension)

        if game_state.player.gold >= final_price:
            gold_spent = final_price
            game_state.player.gold -= final_price

            if self.shop_item.item_type == "card":
                AddCardAction(card=self.shop_item.item).execute()
            elif self.shop_item.item_type == "relic":
                AddRelicAction(relic=self.shop_item.item.idstr).execute()
            elif self.shop_item.item_type == "potion":
                AddRandomPotionAction(character=game_state.player.character).execute()

            self.shop_item.purchased = True

            if self.shop_item.item_type != "relic" and _has_relic("TheCourier"):
                # TheCourier restock: when relic items are bought, restock at 80% price
                self.shop_item.price_multiplier = 0.8

            print(t("ui.shop_bought_item", default=f"Bought {self.shop_item.item.name} for {final_price} gold!"))
            game_state.current_room.enter()
        else:
            print(t("ui.not_enough_gold", default="Not enough gold!"))

        # MawBank effect: track gold spent
        if _has_relic("MawBank"):
            game_state.gold_spent_in_shop = getattr(game_state, "gold_spent_in_shop", 0) + gold_spent


@register("action")
class CardRemovalAction(Action):
    """Action to remove a card using shop service"""

    def __init__(self, shop_room):
        self.shop_room = shop_room

    def execute(self):
        from actions.card import RemoveCardAction
        from actions.display import SelectAction
        from engine.game_state import game_state
        
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
            
            # Build deck selection options
            deck = game_state.player.card_manager.get_pile('deck')
            options = []
            
            for card in deck:
                option = card.display_name
                options.append(
                    Option(
                        name = option,
                        actions = [
                            RemoveCardAction(card=card, src_pile='deck'),
                        ]
                    )
                )
            
            select_action = SelectAction(
                title=LocalStr("ui.choose_cards_to_remove"),
                options=options
            )
            
            # Return SelectAction to be added to caller's action_queue
            self.action_queue.add_action(select_action)


@register("action")
class LeaveShopAction(Action):
    """Action to leave of shop"""

    def execute(self):
        from engine.game_state import game_state
        # MawBank effect: gain 10% of gold spent as interest
        if _has_relic("MawBank"):
            gold_spent = getattr(game_state, "gold_spent_in_shop", 0)
            if gold_spent > 0:
                interest = gold_spent // 10  # 10% of spent gold
                game_state.player.gold += interest
                print(t("ui.maw_bank_interest", default=f"MawBank: Gained {interest} gold interest!"))
            # Reset gold spent for next shop
            game_state.gold_spent_in_shop = 0

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