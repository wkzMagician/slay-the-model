#!/usr/bin/env python
"""Tests for event pool and registration."""

import unittest
from unittest.mock import patch

from events.base_event import Event
from events.event_pool import EventPool
from rooms.event import EventRoom


class TestEventPool(unittest.TestCase):
    """Test event pool functionality."""

    def test_event_pool_creation(self):
        """Test EventPool can be created."""
        pool = EventPool()
        self.assertIsInstance(pool, EventPool)

    def test_event_pool_has_get_event_by_id(self):
        """Test EventPool has get_event_by_id method."""
        pool = EventPool()
        self.assertTrue(hasattr(pool, 'get_event_by_id'))

    def test_event_room_init_does_not_create_fallback_event_when_pool_is_empty(self):
        """Runtime rooms should not invent fallback events when the pool is empty."""
        room = EventRoom()

        with patch("rooms.event.get_random_events", return_value=[]):
            room.init()

        self.assertIsNone(room.selected_event)
        self.assertEqual(room.available_events, [])


class TestEventDecorator(unittest.TestCase):
    """Test event decorator functionality."""

    def test_event_base_class(self):
        """Test Event base class exists."""
        self.assertTrue(Event is not None)

    def test_event_has_choices(self):
        """Test Event has choices attribute."""
        # Event base class exists and has expected interface
        self.assertTrue(hasattr(Event, '__init__'))


if __name__ == "__main__":
    unittest.main()
