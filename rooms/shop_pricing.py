"""Pure pricing helpers for shop items and services."""
from utils.compatible_random import float32


def compute_card_removal_price(
    base_price,
    has_membership_card=False,
    has_the_courier=False,
    has_smiling_mask=False,
):
    """Compute the current card removal service price."""
    if has_smiling_mask:
        return 50

    price = int(base_price)
    if has_membership_card:
        price = int(price * 0.5)
    if has_the_courier:
        price = int(price * 0.8)
    return price



def compute_shop_price(
    base_price,
    ascension_level=0,
    discount: float = 0,
    has_membership_card=False,
    has_the_courier=False,
    has_smiling_mask=False,
    item_type=None,
    card_restock=False,
):
    """Compute the final shop price after ascension and relic modifiers."""
    if card_restock and item_type == "card":
        # Original setPrice applies card restock modifiers before its final cast.
        price = float32(base_price)
        if has_the_courier:
            price = float32(price * float32(0.8))
        if has_membership_card:
            price = float32(price * float32(0.5))
        return int(price)

    price = int(base_price)

    if ascension_level >= 16:
        price = int(price * 1.1)

    if discount > 0:
        price = int(price * (1 - discount))

    if item_type in {"remove", "card_removal"}:
        return compute_card_removal_price(
            base_price=price,
            has_membership_card=has_membership_card,
            has_the_courier=has_the_courier,
            has_smiling_mask=has_smiling_mask,
        )

    if has_membership_card:
        price = int(price * 0.5)

    if has_the_courier:
        price = int(price * 0.8)

    return price
