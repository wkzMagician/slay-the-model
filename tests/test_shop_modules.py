"""Tests for extracted shop helper modules."""

from types import SimpleNamespace

from actions.misc import LeaveRoomAction

from rooms.shop_menu import build_shop_menu
from rooms.shop_pricing import compute_card_removal_price, compute_shop_price
from rooms.shop_state import (
    ShopItem,
    game_state_has_relic,
    generate_shop_items,
    restock_shop_item,
)
from utils.types import RarityType


class _DummyCard:
    def __init__(self, label="Dummy Strike", rarity=RarityType.COMMON):
        self.label = label
        self.rarity = rarity

    def info(self):
        return self.label


class _DummyPotion:
    def __init__(self, label="Potion"):
        self.label = label

    def info(self):
        return self.label


class _DummyRelic:
    def __init__(self, idstr="dummy_relic", name="Dummy Relic"):
        self.idstr = idstr
        self.name = name

    def info(self):
        return self.name


class _DeterministicRng:
    def __init__(self, random_values, randint_values):
        self._random_values = iter(random_values)
        self._randint_values = iter(randint_values)

    def random(self):
        return next(self._random_values)

    def randint(self, low, high):
        value = next(self._randint_values)
        assert low <= value <= high
        return value

    def choice(self, values):
        return values[0]



def test_shop_pricing_applies_membership_discount():
    price = compute_shop_price(base_price=100, has_membership_card=True)
    assert price == 50



def test_card_removal_price_uses_smiling_mask_override():
    price = compute_card_removal_price(
        base_price=75,
        has_membership_card=True,
        has_smiling_mask=True,
    )
    assert price == 50



def test_shop_menu_builds_leave_option():
    menu = build_shop_menu(
        title="shop-title",
        localize=lambda key, **kwargs: key,
        items=[ShopItem("card", _DummyCard(), 100)],
        player_gold=200,
        ascension_level=0,
        card_removal_price=75,
        card_removal_used=False,
        has_smiling_mask=False,
        has_membership_card=False,
        has_the_courier=False,
        room=object(),
    )

    assert any(isinstance(option.actions[0], LeaveRoomAction) for option in menu.options)



def test_game_state_has_relic_normalizes_name_variants():
    game_state = SimpleNamespace(
        player=SimpleNamespace(
            relics=[_DummyRelic(idstr="MembershipCard", name="Membership Card")]
        )
    )

    assert game_state_has_relic("membership card", game_state)
    assert game_state_has_relic("membership_card", game_state)
    assert game_state_has_relic("membership-card", game_state)



def test_generate_shop_items_builds_expected_inventory_shape_and_price_bands():
    player = SimpleNamespace(namespace="silent", relics=[])
    cards = iter(
        [
            _DummyCard("Atk1", RarityType.COMMON),
            _DummyCard("Atk2", RarityType.UNCOMMON),
            _DummyCard("Skill1", RarityType.RARE),
            _DummyCard("Skill2", RarityType.COMMON),
            _DummyCard("Power1", RarityType.UNCOMMON),
            _DummyCard("Colorless U", RarityType.UNCOMMON),
            _DummyCard("Colorless R", RarityType.RARE),
        ]
    )
    potion_calls = []
    relic_calls = []
    rng = _DeterministicRng(
        random_values=[0.1, 0.8, 0.95, 0.2, 0.7],
        randint_values=[45, 68, 135, 50, 83, 3, 81, 162, 48, 71, 95, 143, 238, 150],
    )

    items = generate_shop_items(
        player=player,
        rng=rng,
        card_provider=lambda **kwargs: next(cards),
        potion_provider=lambda **kwargs: potion_calls.append(kwargs) or _DummyPotion(),
        relic_provider=lambda **kwargs: relic_calls.append(kwargs) or _DummyRelic(),
    )

    assert len(items) == 13
    assert [item.item_type for item in items].count("card") == 7
    assert [item.item_type for item in items].count("potion") == 3
    assert [item.item_type for item in items].count("relic") == 3
    assert sum(1 for item in items[:5] if item.discount == 0.5) == 1
    assert [item.base_price for item in items[:8]] == [45, 68, 135, 50, 83, 81, 162, 48]
    assert potion_calls == [
        {"characters": ["silent"], "rarities": [RarityType.COMMON]},
        {"characters": ["silent"], "rarities": [RarityType.UNCOMMON]},
        {"characters": ["silent"], "rarities": [RarityType.RARE]},
    ]
    assert relic_calls[-1] == {"rarities": [RarityType.SHOP]}



def test_build_shop_menu_filters_unaffordable_items_and_uses_card_removal_pricing():
    menu = build_shop_menu(
        title="shop-title",
        localize=lambda key, **kwargs: (key, kwargs),
        items=[ShopItem("card", _DummyCard(), 100), ShopItem("potion", _DummyPotion(), 30)],
        player_gold=50,
        ascension_level=0,
        card_removal_price=75,
        card_removal_used=False,
        has_smiling_mask=True,
        has_membership_card=False,
        has_the_courier=False,
        room=object(),
    )

    option_names = [option.name[0] for option in menu.options]
    removal_action = menu.options[0].actions[0]

    assert option_names == ["remove_card", "buy_potion", "leave"]
    assert removal_action.shop_item.base_price == 50



def test_restock_shop_item_uses_same_potion_namespace_rules_as_initial_inventory():
    player = SimpleNamespace(namespace="defect", relics=[])
    shop_item = ShopItem("potion", _DummyPotion("Old Potion"), 48)
    potion_calls = []
    rng = _DeterministicRng(random_values=[0.2], randint_values=[52])

    restock_shop_item(
        shop_item=shop_item,
        player=player,
        rng=rng,
        potion_provider=lambda **kwargs: potion_calls.append(kwargs) or _DummyPotion("New Potion"),
    )

    assert potion_calls == [{"characters": ["defect"], "rarities": [RarityType.COMMON]}]
    assert shop_item.item.info() == "New Potion"
    assert shop_item.base_price == 52
    assert shop_item.discount == 0
    assert shop_item.purchased is False
