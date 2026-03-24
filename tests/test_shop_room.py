"""Test ShopRoom basic functionality."""
import pytest
from rooms.shop import ShopRoom, ShopItem
from utils.types import RoomType, RarityType


class TestShopRoomBasic:
    """Test ShopRoom basic functionality without special relics."""
    
    def test_shop_room_creation(self):
        """Test ShopRoom initialization."""
        shop_room = ShopRoom()
        assert shop_room is not None
        assert shop_room.room_type == RoomType.MERCHANT
        assert shop_room.localization_prefix == "rooms"
        assert shop_room.card_removal_price == 75
        assert not shop_room.card_removal_used
        assert len(shop_room.items) == 0  # Items not generated yet
    
    def test_shop_item_creation(self):
        """Test ShopItem creation."""
        mock_item = "TestCard"
        shop_item = ShopItem("card", mock_item, 100, discount=0.5)
        
        assert shop_item.item_type == "card"
        assert shop_item.item == mock_item
        assert shop_item.base_price == 100
        assert shop_item.discount == 0.5
        assert not shop_item.purchased
    
    def test_shop_item_price_calculation(self):
        """Test ShopItem price calculation."""
        shop_item = ShopItem("card", "TestCard", 100, discount=0)
        
        # Base price
        assert shop_item.get_final_price(ascension_level=0) == 100
        
        # Ascension 16: 10% more expensive
        assert shop_item.get_final_price(ascension_level=16) == 110
        
        # With 50% discount
        shop_item.discount = 0.5
        assert shop_item.get_final_price(ascension_level=0) == 50
    
    def test_relic_check_without_relics(self):
        """Test _has_relic returns False when player has no relics."""
        from rooms.shop import _has_relic
        
        assert not _has_relic("AnyRelic")
        assert not _has_relic("")
    
    def test_shop_does_not_keep_action_queue(self):
        """Test ShopRoom does not keep a room-local action queue."""
        shop_room = ShopRoom()
        assert not hasattr(shop_room, "action_queue")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
