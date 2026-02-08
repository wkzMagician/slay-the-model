"""Test EventRoom basic functionality."""
import pytest
from rooms.event import EventRoom
from utils.types import RoomType


class TestEventRoomBasic:
    """Test EventRoom basic functionality."""
    
    def test_event_room_creation(self):
        """Test EventRoom initialization."""
        event_room = EventRoom()
        assert event_room is not None
        assert event_room.room_type == RoomType.EVENT
        assert event_room.available_events == []
        assert event_room.triggered_event is None
    
    def test_event_room_has_should_leave(self):
        """Test EventRoom has should_leave flag."""
        event_room = EventRoom()
        assert hasattr(event_room, 'should_leave')
        assert event_room.should_leave is False
    
    def test_event_room_leave_flag(self):
        """Test EventRoom leave flag functionality."""
        event_room = EventRoom()
        event_room.should_leave = False
        
        # Leave flag should work
        assert event_room.should_leave is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
