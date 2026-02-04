"""
Unit tests for Event Pool system.
"""
import unittest
from events.base_event import Event
from events.event_pool import EventPool, EventMetadata, register_event
from engine.game_state import game_state


class MockEvent(Event):
    """Mock event for testing"""
    
    def trigger(self) -> str:
        return None


class TestEventPool(unittest.TestCase):
    """Test cases for EventPool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pool = EventPool()
    
    def test_register_event(self):
        """Test event registration"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="test_event",
            floors='early',
            weight=100,
            is_unique=False
        )
        
        # Check event is in registry
        self.assertIn("test_event", self.pool._event_registry)
        
        # Check metadata
        metadata = self.pool._event_registry["test_event"]
        self.assertEqual(metadata.event_class, MockEvent)
        self.assertEqual(metadata.event_id, "test_event")
        self.assertEqual(metadata.floors, 'early')
        self.assertEqual(metadata.weight, 100)
        self.assertFalse(metadata.is_unique)
    
    def test_floor_pool_assignment(self):
        """Test event is added to correct floor pools"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="early_event",
            floors='early',
            weight=100
        )
        
        self.assertIn("early_event", self.pool._floor_pools['early'])
        self.assertNotIn("early_event", self.pool._floor_pools['mid'])
    
    def test_all_floors_assignment(self):
        """Test event with 'all' floors is added to all pools"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="all_floors_event",
            floors='all',
            weight=100
        )
        
        for pool_name in self.pool._floor_pools:
            self.assertIn("all_floors_event", self.pool._floor_pools[pool_name])
    
    def test_get_available_events(self):
        """Test getting available events for a floor"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="early_event",
            floors='early',
            weight=100
        )
        
        available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].event_id, "early_event")
    
    def test_available_events_filters_by_floor(self):
        """Test that only events for current floor are available"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="early_event",
            floors='early',
            weight=100
        )
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="late_event",
            floors='late',
            weight=100
        )
        
        # Early floor should only have early event
        early_available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(early_available), 1)
        self.assertEqual(early_available[0].event_id, "early_event")
        
        # Late floor should only have late event
        late_available = self.pool.get_available_events(floor=12)
        self.assertEqual(len(late_available), 1)
        self.assertEqual(late_available[0].event_id, "late_event")
    
    def test_unique_event_not_repeated(self):
        """Test that unique events are not available after being used"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="unique_event",
            floors='early',
            weight=100,
            is_unique=True
        )
        
        # Event should be available initially
        available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(available), 1)
        
        # Mark as used
        self.pool.mark_event_used("unique_event")
        
        # Event should no longer be available
        available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(available), 0)
    
    def test_reset_unique_events(self):
        """Test resetting unique events"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="unique_event",
            floors='early',
            weight=100,
            is_unique=True
        )
        
        # Mark as used
        self.pool.mark_event_used("unique_event")
        self.assertTrue(self.pool._event_registry["unique_event"].has_been_used)
        
        # Reset
        self.pool.reset_unique_events()
        self.assertFalse(self.pool._event_registry["unique_event"].has_been_used)
    
    def test_custom_condition_filter(self):
        """Test events filtered by custom condition"""
        condition_met = False
        
        def custom_condition():
            return condition_met
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="conditional_event",
            floors='early',
            weight=100,
            requires_condition=custom_condition
        )
        
        # Event not available when condition is False
        available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(available), 0)
        
        # Event available when condition is True
        condition_met = True
        available = self.pool.get_available_events(floor=2)
        self.assertEqual(len(available), 1)
    
    def test_get_random_event(self):
        """Test getting random event"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="event1",
            floors='early',
            weight=100
        )
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="event2",
            floors='early',
            weight=100
        )
        
        # Should return an event class
        event_class = self.pool.get_random_event(floor=2)
        self.assertIsNotNone(event_class)
        self.assertIn(event_class, [MockEvent])
    
    def test_get_event_by_id(self):
        """Test getting event by ID"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="test_event",
            floors='early',
            weight=100
        )
        
        event_class = self.pool.get_event_by_id("test_event")
        self.assertEqual(event_class, MockEvent)
        
        # Non-existent event should return None
        event_class = self.pool.get_event_by_id("nonexistent")
        self.assertIsNone(event_class)


class TestEventDecorator(unittest.TestCase):
    """Test cases for @register_event decorator"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import fresh event pool for each test
        from events.event_pool import event_pool
        self.pool = event_pool
    
    def test_decorator_registration(self):
        """Test decorator registers event"""
        @register_event(
            event_id="decorated_event",
            floors='mid',
            weight=150,
            is_unique=True
        )
        class DecoratedEvent(Event):
            def trigger(self) -> str:
                return None
        
        # Check event is registered
        self.assertIn("decorated_event", self.pool._event_registry)
        
        metadata = self.pool._event_registry["decorated_event"]
        self.assertEqual(metadata.event_class, DecoratedEvent)
        self.assertEqual(metadata.floors, 'mid')
        self.assertEqual(metadata.weight, 150)
        self.assertTrue(metadata.is_unique)


class TestEventMetadata(unittest.TestCase):
    """Test cases for EventMetadata"""
    
    def test_metadata_initialization(self):
        """Test EventMetadata initialization"""
        metadata = EventMetadata(
            event_class=MockEvent,
            event_id="test",
            floors='late',
            weight=200,
            is_unique=True
        )
        
        self.assertEqual(metadata.event_class, MockEvent)
        self.assertEqual(metadata.event_id, "test")
        self.assertEqual(metadata.floors, 'late')
        self.assertEqual(metadata.weight, 200)
        self.assertTrue(metadata.is_unique)
        self.assertFalse(metadata.has_been_used)


if __name__ == '__main__':
    unittest.main()