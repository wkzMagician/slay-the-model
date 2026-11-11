"""Shop inventory state helpers."""
from engine.random_streams import get_rng, route_domains

from utils.random import get_random_card, get_random_potion, get_random_relic
from utils.types import CardType, RarityType
from utils.compatible_random import float32, java_round_float

from rooms.shop_pricing import compute_shop_price


class ShopItem:
    """Represents an item for sale in the shop."""

    def __init__(self, item_type, item, base_price, discount: float = 0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False
        self.card_restock = False
        self.restocked = False
        self.quoted_price: int | None = None

    def get_final_price(self, ascension_level=0):
        """Calculate the final price using only local item state."""
        quoted_price = getattr(self, "quoted_price", None)
        if quoted_price is not None:
            return quoted_price
        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            item_type=self.item_type,
            card_restock=getattr(self, "card_restock", False),
            restocked=getattr(self, "restocked", False),
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

        quoted_price = getattr(self, "quoted_price", None)
        if quoted_price is not None:
            return quoted_price
        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            has_membership_card=bool(has_membership_card),
            has_the_courier=bool(has_the_courier),
            has_smiling_mask=bool(has_smiling_mask),
            item_type=self.item_type,
            card_restock=getattr(self, "card_restock", False),
            restocked=getattr(self, "restocked", False),
        )

    def prepare_price(self, ascension_level, player):
        """Freeze this slot's current quote once until a discount or restock."""
        self.quoted_price = self.get_final_price_with_modifiers(
            ascension_level,
            has_membership_card=game_state_has_relic("MembershipCard", player=player),
            has_the_courier=game_state_has_relic("TheCourier", player=player),
            has_smiling_mask=game_state_has_relic("SmilingMask", player=player),
        )




def normalize_relic_key(value):
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")



def game_state_has_relic(relic_key, game_state=None, *, player=None):
    """Check whether the current player has a relic by id or name."""
    player = player if player is not None else getattr(game_state, "player", None)
    if player is None:
        return False

    target = normalize_relic_key(relic_key)
    for relic in getattr(player, "relics", []):
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
    rarity_roll = rng.random_int(0, 99)
    if rarity_roll < 65:
        return RarityType.COMMON
    if rarity_roll < 90:
        return RarityType.UNCOMMON
    return RarityType.RARE



def roll_relic_rarity(rng):
    rarity_roll = rng.random()
    if rarity_roll < 0.50:
        return RarityType.COMMON
    if rarity_roll < 0.83:
        return RarityType.UNCOMMON
    return RarityType.RARE



def _card_price(rarity, rng, *, colorless=False):
    base = {RarityType.STARTER: 9999, RarityType.COMMON: 50,
            RarityType.UNCOMMON: 75, RarityType.RARE: 150, RarityType.SPECIAL: 9999}.get(rarity, 0)
    price = float32(base * rng.random_float(0.9, 1.1))
    return float32(price * float32(1.2)) if colorless else price


def get_card_price(rarity, rng):
    return int(_card_price(rarity, rng))


def roll_card_rarity(rng):
    from engine.card_rewards import roll_rarity
    return roll_rarity(rng, "shop", use_offset=True)


def get_colorless_card_price(rarity, rng):
    return int(_card_price(rarity, rng, colorless=True))


def get_potion_price(rarity, rng):
    base = {RarityType.COMMON: 50, RarityType.UNCOMMON: 75, RarityType.RARE: 100}.get(rarity, 999)
    return java_round_float(float32(base * rng.random_float(0.95, 1.05)))


def get_relic_price(rarity, rng):
    base = {RarityType.STARTER: 300, RarityType.COMMON: 150, RarityType.UNCOMMON: 250,
            RarityType.RARE: 300, RarityType.SHOP: 150, RarityType.SPECIAL: 400,
            RarityType.BOSS: 999}.get(rarity, -1)
    return java_round_float(float32(base * rng.random_float(0.95, 1.05)))


def _relic_price_rarity(relic, fallback):
    from relics.pools import definitions
    row = definitions().get(getattr(relic, "idstr", None))
    return RarityType[row["tier"]] if row else getattr(relic, "rarity", fallback)


def _shop_card(card_type, rarity, namespaces, card_provider):
    tiers = [rarity]
    if card_type == CardType.POWER:
        tiers = {
            RarityType.COMMON: [RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            RarityType.UNCOMMON: [RarityType.UNCOMMON, RarityType.RARE],
            RarityType.RARE: [RarityType.RARE, RarityType.UNCOMMON],
        }.get(rarity, tiers)
    # Each empty tier is checked once. An exhausted extension pool returns None.
    for tier in tiers:
        card = card_provider(pool_kind="shop", rarities=[tier], card_types=[card_type], namespaces=namespaces)
        if card is not None:
            return card
    return None


@route_domains(card_random="card")
def generate_colored_cards(player, card_provider=get_random_card, rng=None):
    """Generate 5 colored cards for the shop."""
    from engine.card_pools import original_id

    card_namespaces = build_card_namespaces(player)
    rng = rng if rng is not None else get_rng("card")
    cards = []

    for card_type, count in ((CardType.ATTACK, 2), (CardType.SKILL, 2), (CardType.POWER, 1)):
        previous_id = None
        for _ in range(count):
            while True:
                rarity = roll_card_rarity(rng)
                card = _shop_card(card_type, rarity, card_namespaces, card_provider)
                if card is None:
                    break
                if getattr(card, "namespace", None) != "colorless" and original_id(card) != previous_id:
                    break
            if card is not None:
                cards.append(card)
                previous_id = original_id(card)

    return cards



@route_domains(card_random="card")
def generate_colorless_cards(card_provider=get_random_card):
    """Generate 2 colorless cards for the shop."""
    cards = []

    uncommon_card = card_provider(
        pool_kind="shop",
        rarities=[RarityType.UNCOMMON],
        card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
        namespaces=["colorless"],
    )
    if uncommon_card:
        cards.append(uncommon_card)

    rare_card = card_provider(
        pool_kind="shop",
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
    from engine.card_pools import original_rarity

    explicit_rng = rng
    rng = rng if rng is not None else get_rng("merchant")
    items = []
    namespace = getattr(player, "namespace", None) or "ironclad"

    colored_cards = generate_colored_cards(player=player, card_provider=card_provider, rng=explicit_rng)
    colorless_cards = generate_colorless_cards(card_provider=card_provider)
    colored_start_idx = len(items)
    for card in colored_cards:
        if card is None:
            raise ValueError("unable to get card")
        items.append(ShopItem("card", card, get_card_price(original_rarity(card), rng)))

    colored_end_idx = len(items)
    for card in colorless_cards:
        items.append(ShopItem("card", card, get_colorless_card_price(original_rarity(card), rng)))

    if colored_end_idx > colored_start_idx:
        discounted_index = rng.randint(colored_start_idx, colored_end_idx - 1)
        items[discounted_index].discount = 0.5

    for _ in range(2):
        rarity = roll_relic_rarity(rng)
        relic = relic_provider(rarities=[rarity], from_end=True)
        items.append(ShopItem("relic", relic, get_relic_price(_relic_price_rarity(relic, rarity), rng)))

    shop_relic = relic_provider(rarities=[RarityType.SHOP], from_end=True)
    items.append(ShopItem("relic", shop_relic, get_relic_price(_relic_price_rarity(shop_relic, RarityType.SHOP), rng)))
    for _ in range(3):
        rarity = roll_potion_rarity(explicit_rng if explicit_rng is not None else get_rng("potion"))
        potion = potion_provider(characters=[namespace], rarities=[rarity])
        items.append(ShopItem("potion", potion, get_potion_price(getattr(potion, "rarity", rarity), rng)))
    return items



@route_domains(card_random="card")
def restock_shop_item(
    shop_item,
    player,
    rng=None,
    card_provider=get_random_card,
    potion_provider=get_random_potion,
    relic_provider=get_random_relic,
):
    """Replace a purchased shop slot with a fresh item using the same source-of-truth rules."""
    from engine.card_pools import original_rarity

    if not player or not shop_item:
        return

    explicit_rng = rng
    rng = rng if rng is not None else get_rng("merchant")
    namespace = getattr(player, "namespace", None) or "ironclad"

    if shop_item.item_type == "card":
        namespace = getattr(getattr(shop_item, "item", None), "namespace", None)
        if namespace == "colorless":
            rarity = RarityType.RARE if rng.random() < float32(0.3) else RarityType.UNCOMMON
            new_item = card_provider(
                pool_kind="shop",
                rarities=[rarity],
                card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
                namespaces=["colorless"],
            )
            base_price = _card_price(original_rarity(new_item), rng, colorless=True) if new_item else None
        else:
            card_type = getattr(getattr(shop_item, "item", None), "card_type", None) or rng.choice([CardType.ATTACK, CardType.SKILL, CardType.POWER])
            rarity = roll_card_rarity(rng)
            new_item = _shop_card(card_type, rarity, build_card_namespaces(player), card_provider)
            base_price = _card_price(original_rarity(new_item), rng) if new_item else None
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = base_price
        shop_item.card_restock = True
    elif shop_item.item_type == "potion":
        rarity = roll_potion_rarity(explicit_rng if explicit_rng is not None else get_rng("potion"))
        new_item = potion_provider(characters=[namespace], rarities=[rarity])
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = get_potion_price(getattr(new_item, "rarity", rarity), rng)
    elif shop_item.item_type == "relic":
        from relics.global_relics.common import MawBank, SmilingMask
        from relics.global_relics.rare import OldCoin
        from relics.global_relics.uncommon import TheCourier

        rarity = roll_relic_rarity(rng)
        new_item = relic_provider(rarities=[rarity], from_end=True)
        while isinstance(new_item, (OldCoin, SmilingMask, MawBank, TheCourier)):
            rarity = roll_relic_rarity(rng)
            new_item = relic_provider(rarities=[rarity], from_end=True)
        if not new_item:
            return
        shop_item.item = new_item
        shop_item.base_price = get_relic_price(_relic_price_rarity(new_item, rarity), rng)
    else:
        return

    was_quoted = getattr(shop_item, "quoted_price", None) is not None
    shop_item.discount = 0
    shop_item.purchased = False
    shop_item.restocked = True
    shop_item.quoted_price = None
    if was_quoted:
        shop_item.prepare_price(0, player)
