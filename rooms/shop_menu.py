"""Shop menu construction helpers."""
from actions.display import InputRequestAction
from actions.misc import BuyItemAction, LeaveRoomAction
from utils.option import Option

from rooms.shop_pricing import compute_card_removal_price
from rooms.shop_state import ShopItem



def _build_item_label(localize, item, final_price):
    if item.item_type == "card":
        return localize("buy_card", card=item.item.info(), price=final_price)
    if item.item_type == "relic":
        return localize("buy_relic", relic=item.item.info(), price=final_price)
    if item.item_type == "potion":
        return localize("buy_potion", potion=item.item.info(), price=final_price)
    return localize("buy_item", price=final_price)



def build_shop_menu(
    title,
    localize,
    items,
    player_gold,
    ascension_level,
    card_removal_price,
    card_removal_used,
    has_smiling_mask=False,
    has_membership_card=False,
    has_the_courier=False,
    room=None,
):
    """Build an input request for the current shop state."""
    options = []

    if not card_removal_used:
        removal_price = compute_card_removal_price(
            base_price=card_removal_price,
            has_membership_card=has_membership_card,
            has_the_courier=has_the_courier,
            has_smiling_mask=has_smiling_mask,
        )
        if player_gold is None or player_gold >= removal_price:
            removal_item = ShopItem("card_removal", None, removal_price)
            options.append(
                Option(
                    name=localize("remove_card", price=removal_price),
                    actions=[BuyItemAction(removal_item, -1)],
                )
            )

    for idx, shop_item in enumerate(items):
        if shop_item.purchased or shop_item.item is None:
            continue

        final_price = shop_item.get_final_price_with_modifiers(
            ascension_level=ascension_level,
            has_membership_card=has_membership_card,
            has_the_courier=has_the_courier,
            has_smiling_mask=has_smiling_mask,
        )
        if player_gold is not None and player_gold < final_price:
            continue

        options.append(
            Option(
                name=_build_item_label(localize, shop_item, final_price),
                actions=[BuyItemAction(shop_item, idx)],
            )
        )

    options.append(
        Option(
            name=localize("leave"),
            actions=[LeaveRoomAction(room=room)],
        )
    )

    return InputRequestAction(title=title, options=options)
