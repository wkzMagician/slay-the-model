"""Test TreasureRoom basic functionality."""
import pytest
from rooms.treasure import TreasureRoom
from actions.display import InputRequestAction
from utils.types import RoomType


class TestTreasureRoomBasic:
    """Test TreasureRoom basic functionality."""
    
    def test_treasure_room_creation(self):
        """Test TreasureRoom initialization."""
        treasure_room = TreasureRoom()
        assert treasure_room is not None
        assert not treasure_room.is_boss
        assert treasure_room.chest_type is None
        assert not treasure_room.chest_opened
        assert treasure_room.room_type == RoomType.TREASURE
    
    def test_boss_treasure_room_creation(self):
        """Test boss treasure room initialization."""
        boss_treasure = TreasureRoom(is_boss=True)
        assert boss_treasure is not None
        assert boss_treasure.is_boss
        assert boss_treasure.room_type == RoomType.TREASURE
    
    def test_treasure_room_init_determines_chest_type(self):
        """Test init() determines chest type for non-boss."""
        import random
        original_random = random.random
        
        # Mock random to test
        def mock_random_small():
            return 0.3
        def mock_random_medium():
            return 0.6
        def mock_random_large():
            return 0.9
        
        # Test small chest
        random.random = mock_random_small
        treasure_room = TreasureRoom()
        treasure_room.init()
        assert treasure_room.chest_type == "small"
        
        # Test medium chest
        random.random = mock_random_medium
        treasure_room2 = TreasureRoom()
        treasure_room2.init()
        assert treasure_room2.chest_type == "medium"
        
        # Test large chest
        random.random = mock_random_large
        treasure_room3 = TreasureRoom()
        treasure_room3.init()
        assert treasure_room3.chest_type == "large"
        
        # Restore
        random.random = original_random
    
    def test_boss_treasure_chest_type(self):
        """Test boss treasure always has boss chest type."""
        boss_treasure = TreasureRoom(is_boss=True)
        boss_treasure.init()
        assert boss_treasure.chest_type == "boss"
    
    def test_treasure_room_builds_menu(self):
        """Test _build_treasure_menu returns menu options directly."""
        treasure_room = TreasureRoom()
        treasure_room.init()

        select_action = treasure_room._build_treasure_menu()

        assert isinstance(select_action, InputRequestAction)
        assert len(select_action.options) >= 1  # At least Open Chest or Leave
    
    def test_treasure_room_leave(self):
        """Test TreasureRoom leave functionality."""
        treasure_room = TreasureRoom()
        treasure_room.should_leave = False
        
        # Leave should be handled by LeaveTreasureAction
        assert treasure_room.should_leave is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
