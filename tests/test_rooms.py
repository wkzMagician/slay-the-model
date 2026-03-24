"""Tests for room system."""

import unittest
from unittest.mock import Mock

from rooms.combat import CombatRoom
from rooms.rest import RestRoom
from rooms.shop import ShopRoom
from rooms.treasure import TreasureRoom
from rooms.event import EventRoom
from engine.game_state import game_state


class TestRooms(unittest.TestCase):
    """Test room functionality."""

    def setUp(self):
        game_state._initialized = False
        game_state.__init__()
        game_state.player = Mock()

    def test_create_combat_room(self):
        """Test CombatRoom can be created."""
        room = CombatRoom(enemies=[], room_type="MONSTER", encounter_name="test")
        self.assertIsInstance(room, CombatRoom)

    def test_create_rest_room(self):
        """Test RestRoom can be created."""
        room = RestRoom()
        self.assertIsInstance(room, RestRoom)

    def test_create_shop_room(self):
        """Test ShopRoom can be created."""
        room = ShopRoom()
        self.assertIsInstance(room, ShopRoom)

    def test_create_treasure_room(self):
        """Test TreasureRoom can be created."""
        room = TreasureRoom()
        self.assertIsInstance(room, TreasureRoom)

    def test_create_event_room(self):
        """Test EventRoom can be created."""
        room = EventRoom()
        self.assertIsInstance(room, EventRoom)

    def test_create_boss_room(self):
        """Test boss room can be created."""
        room = CombatRoom(enemies=[], room_type="BOSS", encounter_name="test_boss")
        self.assertIsInstance(room, CombatRoom)


if __name__ == "__main__":
    unittest.main()
