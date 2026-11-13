"""Pure pricing helpers for shop items and services."""
from utils.compatible_random import float32, java_round_float


def compute_card_removal_price(
    base_price,
    has_membership_card=False,
    has_the_courier=False,
    has_smiling_mask=False,
    after_removal=False,
):
    """Compute the current card removal service price."""
    if has_smiling_mask:
        return 50

    if after_removal:
        price = float32(base_price)
        if has_the_courier:
            price = float32(price * float32(0.8))
        if has_membership_card:
            price = float32(price * float32(0.5))
        return java_round_float(price)
    # Initial applyDiscount starts from purgeCost for each separate multiplier.
    if has_membership_card:
        return java_round_float(float32(base_price * float32(0.5)))
    if has_the_courier:
        return java_round_float(float32(base_price * float32(0.8)))
    return int(base_price)




def compute_shop_price(
    base_price,
    ascension_level=0,
    discount: float = 0,
    has_membership_card=False,
    has_the_courier=False,
    has_smiling_mask=False,
    item_type=None,
    card_restock=False,
    restocked=False,
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

    if item_type in {"remove", "card_removal"}:
        return compute_card_removal_price(
            base_price, has_membership_card, has_the_courier, has_smiling_mask,
        )
    price = int(base_price)
    if discount > 0:
        price = int(price * (1 - discount))
    if ascension_level >= 16 and not restocked:
        price = java_round_float(float32(price * float32(1.1)))
    if has_the_courier:
        price = java_round_float(float32(price * float32(0.8)))
    if has_membership_card:
        price = java_round_float(float32(price * float32(0.5)))
    return price
