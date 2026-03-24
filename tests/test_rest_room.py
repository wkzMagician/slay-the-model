"""Test RestRoom basic functionality."""
import pytest

from rooms.rest import RestRoom

from player.player import Player

from engine.game_state import game_state, GameState


class TestRestRoomBasic:
    """Test RestRoom basic functionality without special relics."""

    def test_rest_room_creation(self):
        """Test RestRoom initialization."""
        rest_room = RestRoom()
        assert rest_room is not None
        assert rest_room.room_type.value == "Rest Site"
        assert rest_room.localization_prefix == "rooms"

    def test_rest_room_does_not_keep_action_queue(self):
        """Test RestRoom does not keep a room-local action queue."""
        rest_room = RestRoom()
        assert not hasattr(rest_room, "action_queue")

    def test_relic_check_without_relics(self):
        """Test _has_relic returns False when player has no relics."""
        from rooms.rest import _has_relic
        assert not _has_relic("AnyRelic")
        assert not _has_relic("")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
