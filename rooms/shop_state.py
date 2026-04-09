"""Shop inventory state helpers."""
import random

from utils.random import get_random_card, get_random_potion, get_random_relic
from utils.types import CardType, RarityType

from rooms.shop_pricing import compute_shop_price


class ShopItem:
    """Represents an item for sale in the shop."""

    def __init__(self, item_type, item, base_price, discount: float = 0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False

    def get_final_price(self, ascension_level=0):
        """Calculate the final price using only local item state."""
        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            item_type=self.item_type,
        )

    def get_final_price_with_modifiers(
        self,
        ascension_level=0,
        game_state=None,
        has_membership_card=None,
        has_the_courier=None,
        has_smiling_mask=None,
    ):
        """Calculate the final price including relic-based modifiers."""
        if game_state is not None:
            has_membership_card = game_state_has_relic("MembershipCard", game_state)
            has_the_courier = game_state_has_relic("TheCourier", game_state)
            has_smiling_mask = game_state_has_relic("SmilingMask", game_state)

        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            has_membership_card=bool(has_membership_card),
            has_the_courier=bool(has_the_courier),
            has_smiling_mask=bool(has_smiling_mask),
            item_type=self.item_type,
        )



def normalize_relic_key(value):
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")



def game_state_has_relic(relic_key, game_state=None):
    """Check whether the current player has a relic by id or name."""
    if not game_state or not getattr(game_state, "player", None):
        return False

    target = normalize_relic_key(relic_key)
    for relic in getattr(game_state.player, "relics", []):
        relic_id = getattr(relic, "idstr", None)
        if relic_id and normalize_relic_key(relic_id) == target:
            return True
        relic_name = getattr(relic, "name", None)
        if relic_name and normalize_relic_key(relic_name) == target:
            return True
    return False



def build_card_namespaces(player):
    """Return the card namespace restriction for the current player."""
    if not player:
        return ["ironclad"]

    namespace = getattr(player, "namespace", None) or "ironclad"
    if any(getattr(relic, "idstr", None) == "PrismaticShard" for relic in getattr(player, "relics", [])):
        return None
    return [namespace]



def roll_potion_rarity(rng):
    rarity_roll = rng.random()
    if rarity_roll < 0.65:
        return RarityType.COMMON
    if rarity_roll < 0.90:
        return RarityType.UNCOMMON
    return RarityType.RARE



def roll_relic_rarity(rng):
    rarity_roll = rng.random()
    if rarity_roll < 0.50:
        return RarityType.COMMON
    if rarity_roll < 0.83:
        return RarityType.UNCOMMON
    return RarityType.RARE



def get_card_price(rarity, rng):
    if rarity == RarityType.COMMON:
        return rng.randint(45, 55)
    if rarity == RarityType.UNCOMMON:
        return rng.randint(68, 83)
    return rng.randint(135, 165)


def roll_card_rarity(rng):
    rarity_roll = rng.random()
    if rarity_roll < 0.54:
        return RarityType.COMMON
    if rarity_roll < 0.91:
        return RarityType.UNCOMMON
    return RarityType.RARE



def get_colorless_card_price(rarity, rng):
    if rarity == RarityType.UNCOMMON:
        return rng.randint(81, 99)
    if rarity == RarityType.RARE:
        return rng.randint(162, 198)
    return rng.randint(81, 99)



def get_potion_price(rarity, rng):
    if rarity == RarityType.COMMON:
        return rng.randint(48, 53)
    if rarity == RarityType.UNCOMMON:
        return rng.randint(71, 79)
    return rng.randint(95, 105)



def get_relic_price(rarity, rng):
    if rarity == RarityType.COMMON:
        return rng.randint(143, 158)
    if rarity == RarityType.UNCOMMON:
        return rng.randint(238, 263)
    return rng.randint(285, 315)



def generate_colored_cards(player, card_provider=get_random_card, rng=None):
    """Generate 5 colored cards for the shop."""
    card_namespaces = build_card_namespaces(player)
    rng = rng or random
    cards = []
    seen_ids = []

    for _ in range(2):
        rarity = roll_card_rarity(rng)
        card = card_provider(
            rarities=[rarity],
            card_types=[CardType.ATTACK],
            namespaces=card_namespaces,
            exclude_card_ids=seen_ids,
        )
        if card:
            cards.append(card)
            seen_ids.append(getattr(card, "idstr", getattr(card, "label", card.__class__.__name__)))

    for _ in range(2):
        rarity = roll_card_rarity(rng)
        card = card_provider(
            rarities=[rarity],
            card_types=[CardType.SKILL],
            namespaces=card_namespaces,
            exclude_card_ids=seen_ids,
        )
        if card:
            cards.append(card)
            seen_ids.append(getattr(card, "idstr", getattr(card, "label", card.__class__.__name__)))

    rarity = roll_card_rarity(rng)
    card = card_provider(
        rarities=[rarity],
        card_types=[CardType.POWER],
        namespaces=card_namespaces,
        exclude_card_ids=seen_ids,
    )
    if card:
        cards.append(card)

    return cards



def generate_colorless_cards(card_provider=get_random_card):
    """Generate 2 colorless cards for the shop."""
    cards = []

    uncommon_card = card_provider(
        rarities=[RarityType.UNCOMMON],
        card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
        namespaces=["colorless"],
    )
    if uncommon_card:
        cards.append(uncommon_card)

    rare_card = card_provider(
        rarities=[RarityType.RARE],
        card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
        namespaces=["colorless"],
    )
    if rare_card:
        cards.append(rare_card)

    return cards



def generate_shop_items(
    player=None,
    rng=None,
    card_provider=get_random_card,
    potion_provider=get_random_potion,
    relic_provider=get_random_relic,
):
    """Generate the current shop inventory."""
    rng = rng or random
    items = []
    namespace = getattr(player, "namespace", None) or "ironclad"

    colored_cards = generate_colored_cards(player=player, card_provider=card_provider, rng=rng)
    colored_start_idx = len(items)
    for card in colored_cards:
        if card is None:
            raise ValueError("unable to get card")
        items.append(ShopItem("card", card, get_card_price(card.rarity, rng)))

    colored_end_idx = len(items)
    if colored_end_idx > colored_start_idx:
        discounted_index = rng.randint(colored_start_idx, colored_end_idx - 1)
        items[discounted_index].discount = 0.5

    for card in generate_colorless_cards(card_provider=card_provider):
        if card is None:
            continue
        items.append(ShopItem("card", card, get_colorless_card_price(card.rarity, rng)))

    for _ in range(3):
        rarity = roll_potion_rarity(rng)
        potion = potion_provider(characters=[namespace], rarities=[rarity])
        items.append(ShopItem("potion", potion, get_potion_price(rarity, rng)))

    for _ in range(2):
        rarity = roll_relic_rarity(rng)
        relic = relic_provider(rarities=[rarity])
        items.append(ShopItem("relic", relic, get_relic_price(rarity, rng)))

    shop_relic = relic_provider(rarities=[RarityType.SHOP])
    items.append(ShopItem("relic", shop_relic, rng.randint(143, 158)))
    return items



def restock_shop_item(
    shop_item,
    player,
    rng=None,
    card_provider=get_random_card,
    potion_provider=get_random_potion,
    relic_provider=get_random_relic,
):
    """Replace a purchased shop slot with a fresh item using the same source-of-truth rules."""
    if not player or not shop_item:
        return

    rng = rng or random
    namespace = getattr(player, "namespace", None) or "ironclad"

    if shop_item.item_type == "card":
        namespace = getattr(getattr(shop_item, "item", None), "namespace", None)
        if namespace == "colorless":
            rarity = getattr(getattr(shop_item, "item", None), "rarity", RarityType.UNCOMMON)
            if rarity not in {RarityType.UNCOMMON, RarityType.RARE}:
                rarity = RarityType.UNCOMMON
            new_item = card_provider(
                rarities=[rarity, RarityType.RARE] if rarity == RarityType.UNCOMMON else [RarityType.RARE],
                card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
                namespaces=["colorless"],
            )
            base_price = get_colorless_card_price(getattr(new_item, "rarity", rarity), rng) if new_item else None
        else:
            card_type = getattr(getattr(shop_item, "item", None), "card_type", None) or rng.choice([CardType.ATTACK, CardType.SKILL, CardType.POWER])
            rarity = roll_card_rarity(rng)
            new_item = card_provider(
                rarities=[rarity],
                card_types=[card_type],
                namespaces=build_card_namespaces(player),
            )
            base_price = get_card_price(getattr(new_item, "rarity", rarity), rng) if new_item else None
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = base_price
    elif shop_item.item_type == "potion":
        rarity = roll_potion_rarity(rng)
        new_item = potion_provider(characters=[namespace], rarities=[rarity])
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = get_potion_price(rarity, rng)
    elif shop_item.item_type == "relic":
        rarity = roll_relic_rarity(rng)
        new_item = relic_provider(rarities=[rarity])
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = get_relic_price(rarity, rng)
    else:
        return

    shop_item.discount = 0
    shop_item.purchased = False
