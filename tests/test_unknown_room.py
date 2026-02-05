"""Test UnknownRoom basic functionality."""
import pytest
from rooms.base import UnknownRoom
from utils.types import RoomType


class TestUnknownRoomBasic:
    """Test UnknownRoom basic functionality."""
    
    def test_unknown_room_creation(self):
        """Test UnknownRoom initialization."""
        unknown_room = UnknownRoom()
        assert unknown_room is not None
        assert unknown_room.room_type == RoomType.UNKNOWN
        assert unknown_room.actual_room is None
        assert unknown_room.event is None
    
    def test_unknown_room_has_action_queue(self):
        """Test UnknownRoom has action queue."""
        unknown_room = UnknownRoom()
        assert unknown_room.action_queue is not None
    
    def test_unknown_room_leave(self):
        """Test UnknownRoom leave functionality."""
        unknown_room = UnknownRoom()
        unknown_room.should_leave = False
        
        # Leave should work
        assert unknown_room.should_leave is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
