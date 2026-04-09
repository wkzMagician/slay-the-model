"""Tests for shop card removal purchase behavior."""

import unittest
from unittest.mock import patch
from typing import Any, cast

from actions.misc import BuyItemAction
from engine.game_state import game_state
from rooms.shop import ShopItem


class _DummyDisplayName:
    def __init__(self, text: str):
        self.text = text

    def resolve(self) -> str:
        return self.text

    def __str__(self) -> str:
        return self.text


class _DummyCard:
    def __init__(self, name: str = "Dummy Card"):
        self.name = name
        self.display_name = _DummyDisplayName(name)


class _DummyPotion:
    def __init__(self, name: str = "Dummy Potion"):
        self.name = name
        self.display_name = _DummyDisplayName(name)


class _DummyCardManager:
    def __init__(self):
        self.added = []

    def add_to_pile(self, card, pile, pos):
        self.added.append((card, pile, pos))
        return True


class _DummyRelic:
    def __init__(self, relic_id: str):
        self.idstr = relic_id


class _DummyPlayer:
    def __init__(self, gold=100, relics=None):
        self.gold = gold
        self.relics = relics or []
        self.character = "Ironclad"
        self.card_manager = _DummyCardManager()
        self.potions = []
        self.potion_limit = 3


class _DummyRoom:
    def __init__(self, card_removal_price=75):
        self.card_removal_used = False
        self.card_removal_price = card_removal_price


class TestShopRemoveCard(unittest.TestCase):
    def setUp(self):
        game_state._initialized = False
        game_state.__init__()
        cast(Any, game_state).player = _DummyPlayer(gold=100)
        cast(Any, game_state).current_room = _DummyRoom(card_removal_price=75)

    @patch("actions.card.ChooseRemoveCardAction.execute", return_value=None)
    def test_card_removal_spends_gold_and_updates_room_state(self, _):
        item = ShopItem("card_removal", None, 75)

        BuyItemAction(item, -1).execute()

        self.assertEqual(game_state.player.gold, 25)
        assert game_state.current_room is not None
        self.assertTrue(game_state.current_room.card_removal_used)
        self.assertEqual(game_state.current_room.card_removal_price, 100)
        self.assertEqual(game_state.card_removal_price, 100)

    @patch("actions.card.ChooseRemoveCardAction.execute", return_value=None)
    def test_card_removal_with_smiling_mask_does_not_increase_price(self, _):
        game_state.player.relics = [_DummyRelic("SmilingMask")]
        # Smiling Mask 在商店菜单构造时会把删牌价格固定为 50
        item = ShopItem("card_removal", None, 50)

        BuyItemAction(item, -1).execute()

        self.assertEqual(game_state.player.gold, 50)
        assert game_state.current_room is not None
        self.assertTrue(game_state.current_room.card_removal_used)
        self.assertEqual(game_state.current_room.card_removal_price, 75)

    @patch("actions.card.ChooseRemoveCardAction.execute", return_value=None)
    def test_card_removal_with_the_courier_uses_discounted_price(self, _):
        game_state.player.relics = [_DummyRelic("TheCourier")]
        item = ShopItem("card_removal", None, 60)

        BuyItemAction(item, -1).execute()

        self.assertEqual(game_state.player.gold, 40)
        self.assertEqual(game_state.card_removal_price, 100)

    def test_normal_card_purchase_still_spends_gold(self):
        card = _DummyCard("Test Card")
        item = ShopItem("card", card, 50)

        BuyItemAction(item, 0).execute()

        self.assertEqual(game_state.player.gold, 50)
        self.assertTrue(item.purchased)
        self.assertEqual(len(cast(Any, game_state.player.card_manager).added), 1)

    def test_potion_purchase_obtains_displayed_potion(self):
        potion = _DummyPotion("Shown Potion")
        item = ShopItem("potion", potion, 40)

        BuyItemAction(item, 0).execute()

        self.assertEqual(game_state.player.gold, 60)
        self.assertEqual(len(game_state.player.potions), 1)
        self.assertIs(game_state.player.potions[0], potion)


if __name__ == "__main__":
    unittest.main()
