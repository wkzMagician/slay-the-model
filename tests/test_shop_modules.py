"""Tests for extracted shop helper modules."""

from types import SimpleNamespace
from unittest.mock import patch

from actions.misc import LeaveRoomAction

from rooms.shop_menu import build_shop_menu
from rooms.shop_pricing import compute_card_removal_price, compute_shop_price
from rooms.shop_state import (
    ShopItem,
    game_state_has_relic,
    generate_shop_items,
    restock_shop_item,
)
from utils.types import CardType, RarityType


class _DummyCard:
    def __init__(self, label="Dummy Strike", rarity=RarityType.COMMON):
        self.label = label
        self.rarity = rarity
        self.namespace = "silent"
        self.idstr = label

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


def test_card_removal_price_applies_courier_discount():
    price = compute_card_removal_price(
        base_price=75,
        has_membership_card=False,
        has_the_courier=True,
        has_smiling_mask=False,
    )
    assert price == 60


def test_card_removal_price_stacks_membership_and_courier():
    price = compute_card_removal_price(
        base_price=100,
        has_membership_card=True,
        has_the_courier=True,
        has_smiling_mask=False,
    )
    assert price == 40



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
        random_values=[0.1, 0.8, 0.95, 0.2, 0.7, 0.1, 0.8, 0.95, 0.2, 0.7],
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


def test_build_shop_menu_uses_courier_discount_for_card_removal():
    menu = build_shop_menu(
        title="shop-title",
        localize=lambda key, **kwargs: (key, kwargs),
        items=[],
        player_gold=100,
        ascension_level=0,
        card_removal_price=75,
        card_removal_used=False,
        has_smiling_mask=False,
        has_membership_card=False,
        has_the_courier=True,
        room=object(),
    )

    removal_action = menu.options[0].actions[0]
    assert removal_action.shop_item.base_price == 60



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



def test_card_generation_and_restock_share_card_provider_rules_including_prismatic_shard():
    shard_player = SimpleNamespace(namespace="watcher", relics=[_DummyRelic(idstr="PrismaticShard")])
    card_calls = []
    cards = iter(
        [
            _DummyCard("Atk1", RarityType.COMMON),
            _DummyCard("Atk2", RarityType.COMMON),
            _DummyCard("Skill1", RarityType.COMMON),
            _DummyCard("Skill2", RarityType.COMMON),
            _DummyCard("Power1", RarityType.COMMON),
            _DummyCard("Colorless U", RarityType.UNCOMMON),
            _DummyCard("Colorless R", RarityType.RARE),
            _DummyCard("Restocked", RarityType.COMMON),
        ]
    )
    rng = _DeterministicRng(
        random_values=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        randint_values=[45, 45, 45, 45, 45, 0, 81, 162, 48, 48, 48, 143, 143, 143, 45],
    )

    items = generate_shop_items(
        player=shard_player,
        rng=rng,
        card_provider=lambda **kwargs: card_calls.append({k: list(v) if isinstance(v, list) else v for k, v in kwargs.items()}) or next(cards),
        potion_provider=lambda **kwargs: _DummyPotion(),
        relic_provider=lambda **kwargs: _DummyRelic(),
    )
    restock_shop_item(
        shop_item=items[0],
        player=shard_player,
        rng=rng,
        card_provider=lambda **kwargs: card_calls.append({k: list(v) if isinstance(v, list) else v for k, v in kwargs.items()}) or next(cards),
    )

    assert card_calls[:5] == [
        {"rarities": [RarityType.COMMON], "card_types": [CardType.ATTACK], "namespaces": None, "exclude_card_ids": []},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.ATTACK], "namespaces": None, "exclude_card_ids": ["Atk1"]},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.SKILL], "namespaces": None, "exclude_card_ids": ["Atk1", "Atk2"]},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.SKILL], "namespaces": None, "exclude_card_ids": ["Atk1", "Atk2", "Skill1"]},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.POWER], "namespaces": None, "exclude_card_ids": ["Atk1", "Atk2", "Skill1", "Skill2"]},
    ]
    assert card_calls[5:7] == [
        {"rarities": [RarityType.UNCOMMON], "card_types": [CardType.SKILL, CardType.ATTACK, CardType.POWER], "namespaces": ["colorless"]},
        {"rarities": [RarityType.RARE], "card_types": [CardType.SKILL, CardType.ATTACK, CardType.POWER], "namespaces": ["colorless"]},
    ]
    assert card_calls[7] == {
        "rarities": [RarityType.COMMON],
        "card_types": [CardType.ATTACK],
        "namespaces": None,
    }



def test_restock_shop_item_never_requests_shop_relic_rarity():
    player = SimpleNamespace(namespace="ironclad", relics=[])
    shop_item = ShopItem("relic", _DummyRelic("old"), 143)
    relic_calls = []
    rng = _DeterministicRng(random_values=[0.82], randint_values=[260])

    restock_shop_item(
        shop_item=shop_item,
        player=player,
        rng=rng,
        relic_provider=lambda **kwargs: relic_calls.append(kwargs) or _DummyRelic("new"),
    )

    assert relic_calls == [{"rarities": [RarityType.UNCOMMON]}]


def test_restock_colorless_card_preserves_colorless_pool():
    player = SimpleNamespace(namespace="silent", relics=[])
    shop_item = ShopItem("card", _DummyCard("Colorless Old", RarityType.UNCOMMON), 81)
    shop_item.item.namespace = "colorless"
    card_calls = []
    rng = _DeterministicRng(random_values=[], randint_values=[90])

    def provider(**kwargs):
        card_calls.append(kwargs)
        card = _DummyCard("Colorless New", RarityType.UNCOMMON)
        card.namespace = "colorless"
        return card

    restock_shop_item(
        shop_item=shop_item,
        player=player,
        rng=rng,
        card_provider=provider,
    )

    assert card_calls == [{
        "rarities": [RarityType.UNCOMMON, RarityType.RARE],
        "card_types": [CardType.SKILL, CardType.ATTACK, CardType.POWER],
        "namespaces": ["colorless"],
    }]
    assert shop_item.base_price == 90


def test_generate_colored_cards_rolls_rarity_per_slot_instead_of_pooling_all_rarities():
    from rooms.shop_state import generate_colored_cards

    player = SimpleNamespace(namespace="silent", relics=[])
    calls = []

    class _FixedRng:
        def __init__(self):
            self.values = iter([0.10, 0.80, 0.96, 0.20, 0.50])

        def random(self):
            return next(self.values)

    def provider(**kwargs):
        calls.append({k: list(v) if isinstance(v, list) else v for k, v in kwargs.items()})
        return _DummyCard("Card", kwargs["rarities"][0])

    cards = generate_colored_cards(player=player, card_provider=provider, rng=_FixedRng())

    assert len(cards) == 5
    assert calls == [
        {"rarities": [RarityType.COMMON], "card_types": [CardType.ATTACK], "namespaces": ["silent"], "exclude_card_ids": []},
        {"rarities": [RarityType.UNCOMMON], "card_types": [CardType.ATTACK], "namespaces": ["silent"], "exclude_card_ids": ["Card"]},
        {"rarities": [RarityType.RARE], "card_types": [CardType.SKILL], "namespaces": ["silent"], "exclude_card_ids": ["Card", "Card"]},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.SKILL], "namespaces": ["silent"], "exclude_card_ids": ["Card", "Card", "Card"]},
        {"rarities": [RarityType.COMMON], "card_types": [CardType.POWER], "namespaces": ["silent"], "exclude_card_ids": ["Card", "Card", "Card", "Card"]},
    ]
