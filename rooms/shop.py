"""
Shop room implementation - manages purchasing loop.
"""
import random
from actions.card import AddCardAction, ChooseRemoveCardAction
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddRelicAction, AddGoldAction, AddRandomPotionAction
from actions.misc import BuyItemAction, LeaveRoomAction, _has_relic
from utils.result_types import GameStateResult, NoneResult
from engine.game_state import game_state
from localization import LocalStr, t
from utils.option import Option
from utils.random import get_random_card, get_random_relic, get_random_potion
from utils.registry import register
from utils.types import RarityType, CardType, RoomType
from rooms.base import Room, BaseResult
from actions.combat import HealAction, TriggerRelicAction


class ShopItem:
    """Represents an item for sale in the shop"""

    def __init__(self, item_type, item, base_price, discount=0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False

    def get_final_price(self, ascension_level=0):
        """Calculate final price considering ascension and discounts"""
        price = self.base_price
        if ascension_level >= 16:
            price = int(price * 1.1)
        if self.discount > 0:
            price = int(price * (1 - self.discount))
        return price

    def get_final_price_with_modifiers(self, ascension_level=0, game_state=None):
        """Calculate final price with all relic modifiers"""
        final_price = self.get_final_price(ascension_level)

        if game_state and game_state.player:
            # MembershipCard: 50% discount on all items
            if _has_relic("MembershipCard", game_state):
                final_price = int(final_price * 0.5)

            # TheCourier: 80% price on restocked items (after purchase)
            if self.item_type != "relic" and _has_relic("TheCourier", game_state) and self.purchased:
                final_price = int(final_price * 0.8)

            # SmilingMask: card removal always 50 gold
            if self.item_type == "remove" and _has_relic("SmilingMask", game_state):
                final_price = 50

        return final_price

class ShopRoom(Room):
    """Shop room where player can buy cards, relics, potions, and card removal"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = RoomType.MERCHANT
        self.localization_prefix = "rooms"
        self.items = []
        self.card_removal_price = 75
        self.card_removal_used = False
    
    def init(self):
        """Initialize the shop - generate items"""
        self.items = self._generate_items()
    
    def enter(self) -> BaseResult:
        """Enter shop room and handle purchasing loop"""
        # Display shop entry message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="rooms.shop.enter"
        ))

        # Main shop loop
        while not self.should_leave:
            # Build and display shop menu
            self._build_shop_menu()

            # Execute actions
            result = game_state.execute_all_actions()

            if isinstance(result, GameStateResult):
                return result

            # Rebuild menu for next iteration (if not leaving)
            if not self.should_leave:
                game_state.action_queue.clear()

        # Display leaving message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="rooms.shop.leave"
        ))

        # Execute final message
        game_state.execute_all_actions()

        return NoneResult()
    
    def leave(self):
        """Leave the shop room"""
        super().leave()
        # Reset card removal for next visit
        self.card_removal_used = False
    
    def _generate_items(self):
        """Generate shop items"""
        items = []
        character = game_state.player.character if game_state.player else "ironclad"
        ascension = getattr(game_state, 'ascension_level', 0)
        
        # Generate 5 colored cards (2 attacks, 2 skills, 1 power)
        for _ in range(2):
            card = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[CardType.ATTACK],
                namespaces=[character]
            )
            if card is None:
                raise ValueError("unable to get card")
            
            """
5 Colored Cards
This will always be 2 Attacks, 2 Skills, and 1 Power. One random card will have a 50% discount applied.

Prices
Common: 45-55 (50-61Ascension.png 16) Gold
Uncommon: 68-83 (75-91Ascension.png 16) Gold
Rare: 135-165 (149-182Ascension.png 16) Gold
Weight
See how Card weight works here. While shop cards do not affect offset, they are affected by it.

2 Colorless Cards
This will always be an Uncommon Colorless card and a Rare Colorless card. Colorless cards cost 20% more than normal cards.

Prices
Uncommon: 81-99 (89-109Ascension.png 16) Gold
Rare: 162-198 (178-218Ascension.png 16) Gold
3 Potions
Weight
Common Potion: 65%
Uncommon Potion: 25%
Rare Potion: 10%
Prices
Common Potion: 48-53 (52-58Ascension.png 16) Gold
Uncommon Potion: 71-79 (79-87Ascension.png 16) Gold
Rare Potion: 95-105 (105-116Ascension.png 16) Gold
3 Relics
The rightmost slot will always be a Shop Relic. This is the only way to access Shop relics. Even with Courier, only the first Shop Relic is accessible per Shop, and subsequent restocks are non-Shop Relics.

Weight
Common Relic: 50%
Uncommon Relic: 33%
Rare Relic: 17%
Prices
Shop Relic: 143-158 (157-173Ascension.png 16) Gold
Common Relic: 143-158 (157-173Ascension.png 16) Gold
Uncommon Relic: 238-263 (261-289Ascension.png 16) Gold
Rare Relic: 285-315 (314-347Ascension.png 16) Gold
Card Removal Service
Can only be used once per Shop. Its price starts at 75 Gold and increases by 25 each time it is bought at a shop.

Relic Interactions
SmilingMask.png Smiling Mask sets the price of the Card Removal Service to 50 Gold permanently and it will no longer increase the more times you use it.
MembershipCard.png Membership Card makes everything cost 50% less.
SmilingMask.png Smiling Mask overrides the reduced price of Card Removal Service to 50 Gold even with MembershipCard.png Membership Card.
MawBank.png Maw Bank gives 12 Gold every floor. Once you spend gold at the Shop, it will no longer work.
TheCourier.png The Courier makes all cards, relics, and potions sold restock when bought. Prices are also reduced by 20%.
Shop Relics are NOT restocked.
The prices of restocked items will not be affected by AscensionAscension.png 16.
Having both this and MembershipCard.png Membership Card will reduce prices by a total 60%. (0.5 * 0.8 = 0.4) 40% price is a 60% reduction.
            """

            # Correct pricing for colored cards
            if card.rarity == RarityType.COMMON:
                price = random.randint(45, 55)
            elif card.rarity == RarityType.UNCOMMON:
                price = random.randint(68, 83)
            else:  # Rare
                price = random.randint(135, 165)
            items.append(ShopItem("card", card, price))

        for _ in range(2):
            card = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[CardType.SKILL],
                namespaces=[character]
            )
            if card is None:
                raise ValueError("unable to get card")
            # Correct pricing for colored cards
            if card.rarity == RarityType.COMMON:
                price = random.randint(45, 55)
            elif card.rarity == RarityType.UNCOMMON:
                price = random.randint(68, 83)
            else:  # Rare
                price = random.randint(135, 165)
            items.append(ShopItem("card", card, price))

        card = get_random_card(
            rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            card_types=[CardType.POWER],
            namespaces=[character]
        )
        if card is None:
            raise ValueError("unable to get card")
        # Correct pricing for colored cards
        if card.rarity == RarityType.COMMON:
            price = random.randint(45, 55)
        elif card.rarity == RarityType.UNCOMMON:
            price = random.randint(68, 83)
        else:  # Rare
            price = random.randint(135, 165)
        items.append(ShopItem("card", card, price))

        for _ in range(2):
            card = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[CardType.SKILL],
                namespaces=[character]
            )
            if card is None:
                raise ValueError("unable to get card")
            # Correct pricing for colored cards
            if card.rarity == RarityType.COMMON:
                price = random.randint(45, 55)
            elif card.rarity == RarityType.UNCOMMON:
                price = random.randint(68, 83)
            else:  # Rare
                price = random.randint(135, 165)
            items.append(ShopItem("card", card, price))

        card = get_random_card(
            rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            card_types=[CardType.POWER],
            namespaces=[character]
        )
        if card is None:
            raise ValueError("unable to get card")
        # Correct pricing for colored cards
        if card.rarity == RarityType.COMMON:
            price = random.randint(45, 55)
        elif card.rarity == RarityType.UNCOMMON:
            price = random.randint(68, 83)
        else:  # Rare
            price = random.randint(135, 165)
        items.append(ShopItem("card", card, price))
        
        # Apply 50% discount to one random card
        if items:
            random.choice(items[:5]).discount = 0.5
        
        # Generate 2 colorless cards (1 uncommon, 1 rare)
        # Colorless cards cost 20% more than normal cards
        card = get_random_card(rarities=[RarityType.UNCOMMON], card_types=[], namespaces=["colorless"])
        price = random.randint(81, 99)
        items.append(ShopItem("card", card, price))

        card = get_random_card(rarities=[RarityType.RARE], card_types=[], namespaces=["colorless"])
        price = random.randint(162, 198)
        items.append(ShopItem("card", card, price))
        
        # Generate 3 potions
        for _ in range(3):
            rarity_roll = random.random()
            rarity = RarityType.COMMON if rarity_roll < 0.65 else RarityType.UNCOMMON if rarity_roll < 0.90 else RarityType.RARE
            potion = get_random_potion(rarities=[rarity])
            # Correct pricing for potions
            if rarity == RarityType.COMMON:
                price = random.randint(48, 53)
            elif rarity == RarityType.UNCOMMON:
                price = random.randint(71, 79)
            else:  # Rare
                price = random.randint(95, 105)
            items.append(ShopItem("potion", potion, price))
        
        # Generate 3 relics (rightmost is always a shop relic)
        for _ in range(2):
            rarity_roll = random.random()
            rarity = RarityType.COMMON if rarity_roll < 0.50 else RarityType.UNCOMMON if rarity_roll < 0.83 else RarityType.RARE
            relic = get_random_relic(rarities=[rarity])
            # Correct pricing for relics
            if rarity == RarityType.COMMON:
                price = random.randint(143, 158)
            elif rarity == RarityType.UNCOMMON:
                price = random.randint(238, 263)
            else:  # Rare
                price = random.randint(285, 315)
            items.append(ShopItem("relic", relic, price))

        shop_relic = get_random_relic(rarities=[RarityType.SHOP])
        # Shop relic uses same pricing as common relic
        price = random.randint(143, 158)
        items.append(ShopItem("relic", shop_relic, price))
        
        return items
    
    def _build_shop_menu(self):
        """Build shop selection menu"""
        options = []
        ascension = getattr(game_state, 'ascension_level', 0)

        # Card removal service
        if not self.card_removal_used:
            # Use card_removal_price as base, then apply modifiers
            price = self.card_removal_price
            if _has_relic("SmilingMask", game_state):
                price = 50
            elif _has_relic("MembershipCard", game_state):
                price = int(price * 0.5)
            # Only show card removal option if player has enough gold
            if not game_state.player or game_state.player.gold >= price:
                options.append(Option(
                    name=self.local("ShopRoom.remove_card", price=price),
                    actions=[ChooseRemoveCardAction(pile='hand')]
                ))

        # Purchase options for each item
        for idx, shop_item in enumerate(self.items):
            if not shop_item.purchased:
                final_price = shop_item.get_final_price_with_modifiers(ascension, game_state)
                # Only show item if player has enough gold
                if not game_state.player or game_state.player.gold >= final_price:
                    if shop_item.item_type == "card":
                        name = self.local("ShopRoom.buy_card", card=shop_item.item.name, price=final_price)
                    elif shop_item.item_type == "relic":
                        name = self.local("ShopRoom.buy_relic", relic=shop_item.item.name, price=final_price)
                    elif shop_item.item_type == "potion":
                        name = self.local("ShopRoom.buy_potion", potion=shop_item.item.name, price=final_price)
                    else:
                        name = LocalStr(key="Buy for {final_price}")
                    options.append(Option(name=name, actions=[BuyItemAction(shop_item, idx)]))

        # Leave option
        options.append(Option(
            name=self.local("ShopRoom.leave"),
            actions=[LeaveRoomAction(room=self)]
        ))

        # Add to global action queue
        game_state.action_queue.add_action(SelectAction(
            title=self.local("ShopRoom.title"),
            options=options
        ))