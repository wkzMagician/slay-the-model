"""
Event pool system for managing available events.

This module provides a centralized registry and management system
for all game events, allowing UnknownRooms to select events
based on configurable rules and weights.
"""
import random
from typing import Dict, List, Optional, Type, Callable, Any
from engine.game_state import game_state
from utils.registry import list_registered, get_registered_instance


class EventMetadata:
    """
    Metadata for an event in the pool.
    """
    
    def __init__(
        self,
        event_class: Type,
        event_id: str,
        floors: str = 'all',
        weight: int = 100,
        requires_condition: Optional[Callable[[], bool]] = None,
        is_unique: bool = False
    ):
        self.event_class = event_class
        self.event_id = event_id
        self.floors = floors
        self.weight = weight
        self.requires_condition = requires_condition
        self.is_unique = is_unique
        self.has_been_used = False


class EventPool:
    """
    Centralized event pool manager.
    
    Manages available events and provides methods to select events
    based on game state, floors, and other criteria.
    """
    
    def __init__(self):
        # Event registry: maps event class names to their metadata
        self._event_registry: Dict[str, EventMetadata] = {}
        
        # Event pools organized by floor ranges
        self._floor_pools: Dict[str, List[str]] = {
            'early': [],    # Floors 1-4
            'mid': [],      # Floors 5-10
            'late': [],     # Floors 11-15
            'boss': []      # Floor 16
        }
    
    def register_event(
        self,
        event_class: Type,
        event_id: str,
        floors: str = 'all',
        weight: int = 100,
        requires_condition: Optional[Callable[[], bool]] = None,
        is_unique: bool = False
    ):
        """
        Register an event to the pool.
        
        Args:
            event_class: The Event class to register
            event_id: Unique identifier for the event
            floors: When this event can appear ('early', 'mid', 'late', 'boss', 'all')
            weight: Selection weight (higher = more likely to be chosen)
            requires_condition: Optional function that returns True if event can appear
            is_unique: Whether this event can only appear once per run
        """
        metadata = EventMetadata(
            event_class=event_class,
            event_id=event_id,
            floors=floors,
            weight=weight,
            requires_condition=requires_condition,
            is_unique=is_unique
        )
        
        self._event_registry[event_id] = metadata
        
        # Add to appropriate floor pools
        if floors == 'all':
            for pool in self._floor_pools.values():
                pool.append(event_id)
        elif floors in self._floor_pools:
            self._floor_pools[floors].append(event_id)
        else:
            # Add to all pools if floor not recognized
            for pool in self._floor_pools.values():
                pool.append(event_id)
    
    def get_available_events(self, floor: int = 0) -> List[EventMetadata]:
        """
        Get all available events for the current floor.
        
        Args:
            floor: Current floor number
            
        Returns:
            List of available event metadata
        """
        # Determine floor range
        floor_range = self._get_floor_range(floor)
        
        # Get events for this floor range
        event_ids = self._floor_pools.get(floor_range, [])
        
        # Filter by conditions
        available = []
        for event_id in event_ids:
            metadata = self._event_registry.get(event_id)
            if metadata and self._is_event_available(metadata):
                available.append(metadata)
        
        return available
    
    def get_random_event(self, floor: int = 0) -> Optional[Type]:
        """
        Get a random event weighted by their weights.
        
        Args:
            floor: Current floor number
            
        Returns:
            Event class or None if no events available
        """
        available = self.get_available_events(floor)
        
        if not available:
            return None
        
        # Weighted random selection
        events = []
        weights = []
        
        for metadata in available:
            events.append(metadata.event_class)
            weights.append(metadata.weight)
        
        return random.choices(events, weights=weights, k=1)[0]
    
    def get_event_by_id(self, event_id: str) -> Optional[Type]:
        """
        Get an event class by its ID.
        
        Args:
            event_id: Event identifier
            
        Returns:
            Event class or None if not found
        """
        metadata = self._event_registry.get(event_id)
        return metadata.event_class if metadata else None
    
    def mark_event_used(self, event_id: str):
        """
        Mark a unique event as used.
        
        Args:
            event_id: Event identifier
        """
        if event_id in self._event_registry:
            self._event_registry[event_id].has_been_used = True
    
    def _get_floor_range(self, floor: int) -> str:
        """
        Get the floor range category.
        
        Args:
            floor: Floor number
            
        Returns:
            Floor range string
        """
        if floor <= 4:
            return 'early'
        elif floor <= 10:
            return 'mid'
        elif floor <= 15:
            return 'late'
        else:
            return 'boss'
    
    def _is_event_available(self, metadata: 'EventMetadata') -> bool:
        """
        Check if an event is currently available.
        
        Args:
            metadata: Event metadata
            
        Returns:
            True if event can appear
        """
        # Check if unique event was already used
        if metadata.is_unique and metadata.has_been_used:
            return False
        
        # Check custom condition
        if metadata.requires_condition:
            try:
                return metadata.requires_condition()
            except:
                return False
        
        return True
    
    def reset_unique_events(self):
        """Reset all unique events for a new run"""
        for metadata in self._event_registry.values():
            if metadata.is_unique:
                metadata.has_been_used = False


# Global event pool instance
event_pool = EventPool()


# Decorator for registering events
def register_event(
    event_id: str,
    floors: str = 'all',
    weight: int = 100,
    requires_condition: Optional[Callable[[], bool]] = None,
    is_unique: bool = False
):
    """
    Decorator to register an event to the global pool.
    
    Usage:
        @register_event(
            event_id="my_event",
            floors='early',
            weight=150,
            is_unique=True
        )
        class MyEvent(Event):
            def trigger(self) -> str:
                ...
    """
    def decorator(event_class: Type) -> Type:
        event_pool.register_event(
            event_class=event_class,
            event_id=event_id,
            floors=floors,
            weight=weight,
            requires_condition=requires_condition,
            is_unique=is_unique
        )
        return event_class
    return decorator