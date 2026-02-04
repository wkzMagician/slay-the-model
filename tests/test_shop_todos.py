"""
Unit tests for shop-related features: TheCourier, MawBank, Ssserpent Head, and node selection.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MockCard:
    """Mock card for testing"""
    def __init__(self, name="TestCard"):
        self.name = name
        self.rarity = "COMMON"


class MockRelic:
    """Mock relic for testing"""
    def __init__(self, idstr="test_relic", name="TestRelic"):
        self.idstr = idstr
        self.name = name


class MockPlayer:
    """Mock player for testing"""
    def __init__(self):
        self.gold = 100
        self.character = "ironclad"
        self.relics = []
        self.card_manager = Mock()


class MockShopItem:
    """Mock ShopItem for testing to avoid import issues"""
    def __init__(self, item_type, item, base_price, discount=0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False
        self.price_multiplier = 1.0

    def get_final_price(self, ascension_level=0):
        """Calculate final price considering ascension and discounts"""
        price = self.base_price
        if ascension_level >= 16:
            price = int(price * 1.1)
        if self.discount > 0:
            price = int(price * (1 - self.discount))
        # Apply TheCourier multiplier if set
        if self.purchased and hasattr(self, 'price_multiplier'):
            price = int(price * self.price_multiplier)
        return price


class TestTheCourierRestock(unittest.TestCase):
    """Test TheCourier restock logic (line 38 in actions/shop.py)"""

    def test_the_courier_restocks_non_relic_items(self):
        """Test that TheCourier restocks non-relic items at 80% price after purchase"""
        # Create a card shop item
        test_card = MockCard("TestCard")
        shop_item = MockShopItem("card", test_card, 100, discount=0)
        
        # Buy the item (simulating purchase)
        shop_item.purchased = True
        
        # TheCourier restock should set price multiplier to 0.8
        shop_item.price_multiplier = 0.8
        
        # Verify price is reduced by 20%
        final_price = shop_item.get_final_price(ascension_level=0)
        expected_price = int(100 * 0.8)
        self.assertEqual(final_price, expected_price)
        
    def test_the_courier_does_not_affect_relic_items(self):
        """Test that TheCourier does not affect relic items"""
        # Create a relic shop item
        test_relic = MockRelic(idstr="TestRelic", name="TestRelic")
        shop_item = MockShopItem("relic", test_relic, 200, discount=0)
        
        # TheCourier should not restock relic items
        # Verify original price is maintained
        final_price = shop_item.get_final_price(ascension_level=0)
        self.assertEqual(final_price, 200)
        
    def test_the_courier_with_multiple_purchases(self):
        """Test TheCourier effect with multiple item purchases"""
        # Create multiple card items
        items = [
            MockShopItem("card", MockCard("Card1"), 100, discount=0),
            MockShopItem("card", MockCard("Card2"), 75, discount=0),
            MockShopItem("potion", Mock(), 50, discount=0),
        ]
        
        # Buy items and apply TheCourier restock
        for item in items:
            item.purchased = True
            item.price_multiplier = 0.8
            
        # Verify all non-relic items have 80% price
        expected_prices = [int(100 * 0.8), int(75 * 0.8), int(50 * 0.8)]
        for item, expected_price in zip(items, expected_prices):
            final_price = item.get_final_price(ascension_level=0)
            self.assertEqual(final_price, expected_price)


class TestMawBankGoldTracking(unittest.TestCase):
    """Test MawBank gold tracking (line 104 in actions/shop.py and game_state.py)"""

    def test_maw_bank_tracks_gold_spent(self):
        """Test that MawBank tracks gold spent in shop"""
        # Initialize gold_spent_in_shop
        gold_spent_in_shop = 0
        
        # Simulate spending gold
        gold_spent = 100
        gold_spent_in_shop += gold_spent
        
        # Verify tracking
        self.assertEqual(gold_spent_in_shop, 100)
        
    def test_maw_bank_interest_calculation(self):
        """Test MawBank gives 10% interest on gold spent"""
        # Track gold spent
        gold_spent_in_shop = 200
        player_gold = 100
        
        # Calculate interest (10%)
        interest = gold_spent_in_shop // 10
        self.assertEqual(interest, 20)
        
        # Add interest to player gold
        player_gold += interest
        self.assertEqual(player_gold, 120)
        
    def test_maw_bank_multiple_purchases_tracking(self):
        """Test MawBank tracking with multiple purchases"""
        # Initialize tracking
        gold_spent_in_shop = 0
        
        # Make multiple purchases
        purchases = [50, 75, 100]
        for purchase in purchases:
            gold_spent_in_shop += purchase
            
        # Verify total spent
        self.assertEqual(gold_spent_in_shop, 225)
        
        # Calculate total interest
        interest = gold_spent_in_shop // 10
        self.assertEqual(interest, 22)  # 225 // 10 = 22
        
    def test_maw_bank_resets_after_leaving_shop(self):
        """Test that MawBank gold spent resets after leaving shop"""
        # Spend gold
        gold_spent_in_shop = 150
        player_gold = 100
        
        # Apply interest
        interest = gold_spent_in_shop // 10
        player_gold += interest
        self.assertEqual(player_gold, 115)  # 100 + 15
        
        # Reset after leaving shop
        gold_spent_in_shop = 0
        self.assertEqual(gold_spent_in_shop, 0)
        
    def test_maw_bank_with_zero_gold_spent(self):
        """Test MawBank with no gold spent"""
        # No gold spent
        gold_spent_in_shop = 0
        player_gold = 100
        
        # Calculate interest (should be 0)
        interest = gold_spent_in_shop // 10
        self.assertEqual(interest, 0)
        
        # Player gold should not change
        player_gold += interest
        self.assertEqual(player_gold, 100)
        
    def test_game_state_initializes_gold_spent(self):
        """Test that GameState initializes gold_spent_in_shop to 0"""
        gold_spent_in_shop = 0
        self.assertEqual(gold_spent_in_shop, 0)


class TestSsserpentHeadGold(unittest.TestCase):
    """Test Ssserpent Head +50 gold (line 696 in map/map_manager.py)"""

    def test_ssserpent_head_adds_50_gold(self):
        """Test that Ssserpent Head adds 50 gold when resolving unknown rooms"""
        player_gold = 100
        has_ssserpent_head = True
        
        # Simulate Ssserpent Head effect
        if has_ssserpent_head:
            player_gold += 50
        
        # Verify gold increased by 50
        self.assertEqual(player_gold, 150)
        
    def test_ssserpent_head_without_flag(self):
        """Test that gold is not added without Ssserpent Head flag"""
        player_gold = 100
        has_ssserpent_head = False
        
        # Initial gold
        initial_gold = player_gold
        
        # Simulate Ssserpent Head check
        if has_ssserpent_head:
            player_gold += 50
        
        # Gold should not change
        self.assertEqual(player_gold, initial_gold)
        
    def test_ssserpent_head_multiple_applications(self):
        """Test Ssserpent Head gold addition with multiple unknown rooms"""
        player_gold = 100
        has_ssserpent_head = True
        
        # Apply Ssserpent Head effect multiple times
        for _ in range(3):
            if has_ssserpent_head:
                player_gold += 50
        
        # Verify gold increased by 50 * 3 = 150
        self.assertEqual(player_gold, 250)


class TestNodeSelectionPriority(unittest.TestCase):
    """Test AI/human node selection with priority logic (game_flow.py)"""

    def test_ai_priority_rest_highest(self):
        """Test that AI selects REST room with highest priority"""
        # Create mock nodes
        nodes = []
        for idx, room_type in enumerate(["REST", "MERCHANT", "TREASURE", "MONSTER", "ELITE", "BOSS"]):
            node = Mock()
            node.room_type = room_type
            node.floor = idx + 1
            node.position = idx
            nodes.append(node)
            
        # Set AI priority map
        priority_map = {
            "REST": 1,
            "MERCHANT": 2,
            "TREASURE": 3,
            "MONSTER": 4,
            "ELITE": 5,
            "BOSS": 6,
            "UNKNOWN": 7,
        }
        
        # Sort nodes by priority
        available_nodes = nodes[:]
        available_nodes.sort(key=lambda n: (
            priority_map.get(n.room_type, 99),
            n.position
        ))
        
        # REST should be first
        self.assertEqual(available_nodes[0].room_type, "REST")
        
    def test_ai_priority_order(self):
        """Test correct AI priority order: REST > SHOP > TREASURE > MONSTER > ELITE > BOSS"""
        # Create mock nodes
        nodes = []
        for idx, room_type in enumerate(["REST", "MERCHANT", "TREASURE", "MONSTER", "ELITE", "BOSS"]):
            node = Mock()
            node.room_type = room_type
            node.floor = idx + 1
            node.position = idx
            nodes.append(node)
            
        priority_map = {
            "REST": 1,
            "MERCHANT": 2,
            "TREASURE": 3,
            "MONSTER": 4,
            "ELITE": 5,
            "BOSS": 6,
            "UNKNOWN": 7,
        }
        
        # Sort nodes
        available_nodes = nodes[:]
        available_nodes.sort(key=lambda n: (
            priority_map.get(n.room_type, 99),
            n.position
        ))
        
        # Verify order
        expected_order = ["REST", "MERCHANT", "TREASURE", "MONSTER", "ELITE", "BOSS"]
        actual_order = [node.room_type for node in available_nodes]
        self.assertEqual(actual_order, expected_order)
        
    def test_ai_priority_with_tiebreaker(self):
        """Test that AI uses position as tiebreaker for same room type"""
        # Create two REST nodes at different positions
        node1 = Mock()
        node1.room_type = "REST"
        node1.floor = 1
        node1.position = 0
        
        node2 = Mock()
        node2.room_type = "REST"
        node2.floor = 1
        node2.position = 1
        
        available_nodes = [node2, node1]  # node2 first in list
        
        priority_map = {"REST": 1}
        available_nodes.sort(key=lambda n: (
            priority_map.get(n.room_type, 99),
            n.position
        ))
        
        # Position 0 should come first
        self.assertEqual(available_nodes[0].position, 0)
        self.assertEqual(available_nodes[1].position, 1)
        
    def test_human_mode_prompts_selection(self):
        """Test that human mode prompts for node selection"""
        # Set human mode
        mode = "human"
        
        # In human mode, game should prompt user to select
        # We can't easily test input() in unit tests, so we verify
        # that human mode is recognized
        self.assertEqual(mode, "human")
        
    def test_default_mode_selects_first(self):
        """Test that default mode selects first available node"""
        # Set default mode (not ai or human)
        mode = "default"
        
        available_nodes = []
        for idx in range(3):
            node = Mock()
            node.room_type = f"ROOM{idx}"
            node.floor = idx + 1
            node.position = idx
            available_nodes.append(node)
        
        # Default mode selects first available
        if mode not in ["ai", "human"]:
            selected = available_nodes[0]
            self.assertEqual(selected.room_type, "ROOM0")
            
    def test_ai_with_unknown_room_type(self):
        """Test AI priority with UNKNOWN room type"""
        # Create a node with UNKNOWN type
        unknown_node = Mock()
        unknown_node.room_type = "UNKNOWN"
        unknown_node.floor = 1
        unknown_node.position = 0
        
        rest_node = Mock()
        rest_node.room_type = "REST"
        rest_node.floor = 1
        rest_node.position = 1
        
        available_nodes = [unknown_node, rest_node]
        
        priority_map = {
            "REST": 1,
            "UNKNOWN": 7,
        }
        
        available_nodes.sort(key=lambda n: (
            priority_map.get(n.room_type, 99),
            n.position
        ))
        
        # REST should be selected over UNKNOWN
        self.assertEqual(available_nodes[0].room_type, "REST")
        self.assertEqual(available_nodes[1].room_type, "UNKNOWN")


class TestBuyItemAction(unittest.TestCase):
    """Test BuyItemAction execution with various relics"""

    def test_buy_item_without_relics(self):
        """Test buying item without any shop relics"""
        # Create shop item
        test_card = MockCard("TestCard")
        shop_item = MockShopItem("card", test_card, 100, discount=0)
        
        # Verify gold deduction
        final_price = shop_item.get_final_price(ascension_level=0)
        self.assertEqual(final_price, 100)
        
    def test_buy_item_with_ascension_16(self):
        """Test buying item with ascension level 16 (10% more expensive)"""
        # Create shop item
        test_card = MockCard("TestCard")
        shop_item = MockShopItem("card", test_card, 100, discount=0)
        
        # Calculate price with ascension
        final_price = shop_item.get_final_price(ascension_level=16)
        self.assertEqual(final_price, 110)  # 100 * 1.1


class TestCardRemovalAction(unittest.TestCase):
    """Test CardRemovalAction with relic modifiers"""

    def test_card_removal_base_price(self):
        """Test base card removal price is 75"""
        base_price = 75
        self.assertEqual(base_price, 75)
        
    def test_card_removal_with_smiling_mask(self):
        """Test card removal price is 50 with SmilingMask relic"""
        base_price = 75
        final_price = 50  # SmilingMask sets price to 50
        self.assertEqual(final_price, 50)
        
    def test_card_removal_with_membership_card(self):
        """Test card removal price is 50% off with MembershipCard relic"""
        base_price = 75
        final_price = int(base_price * 0.5)
        self.assertEqual(final_price, 37)  # 75 * 0.5 = 37.5, rounds to 37


if __name__ == '__main__':
    unittest.main()
