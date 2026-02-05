# Event Pool System

## Overview

The Event Pool system provides a centralized registry and management system for all game events. It allows UnknownRooms to select events based on configurable rules, floor ranges, and weights.

## Architecture

### Core Components

#### EventPool
Centralized event pool manager that:
- Maintains a registry of all available events
- Organizes events by floor ranges (early, mid, late, boss)
- Provides weighted random selection
- Tracks unique events to prevent repetition

#### EventMetadata
Data class that stores event configuration:
- `event_class`: The Event class to instantiate
- `event_id`: Unique identifier for the event
- `floors`: When event can appear ('early', 'mid', 'late', 'boss', 'all')
- `weight`: Selection weight (higher = more likely)
- `requires_condition`: Optional function to check if event can appear
- `is_unique`: Whether event can only appear once per run
- `has_been_used`: Tracks if unique event was already used

## Floor Ranges

Events are organized into floor ranges:

| Range   | Floors | Description        |
|---------|---------|--------------------|
| early   | 1-4     | Beginning of run    |
| mid     | 5-10    | Middle of run      |
| late    | 11-15   | End of run         |
| boss    | 16       | Boss floor only     |

## Usage

### Registering Events

Use the `@register_event` decorator:

```python
from events.base_event import Event
from events.event_pool import register_event

@register_event(
    event_id="my_custom_event",
    floors='early',
    weight=150,
    is_unique=True
)
class MyCustomEvent(Event):
    def trigger(self) -> str:
        # Event logic here
        return None
```

### Event Parameters

- **event_id** (required): Unique identifier string
- **floors** (optional): When event can appear. Default: 'all'
- **weight** (optional): Selection weight. Default: 100
- **requires_condition** (optional): Function returning bool. Default: None
- **is_unique** (optional): Whether event appears once. Default: False

### Custom Conditions

Events can have custom appearance conditions:

```python
def can_appear():
    from engine.game_state import game_state
    return game_state.player.gold >= 100

@register_event(
    event_id="rich_event",
    floors='mid',
    requires_condition=can_appear
)
class RichEvent(Event):
    def trigger(self) -> str:
        # Only appears if player has 100+ gold
        return None
```

## Integration with UnknownRoom

The `UnknownRoom` automatically uses the event pool:

```python
class UnknownRoom(Room):
    def enter(self) -> str:
        # Get current floor from game state
        floor = game_state.current_floor
        
        # Select random event from pool
        event_class = event_pool.get_random_event(floor)
        
        if event_class:
            # Mark event as used if unique
            event_id = event_class.__name__
            metadata = event_pool._event_registry.get(event_id)
            if metadata and metadata.is_unique:
                event_pool.mark_event_used(event_id)
            
            # Create and trigger event
            event = event_class()
            return event.trigger()
        
        # Fallback if no events available
        return None
```

## API Reference

### EventPool Methods

#### `register_event(event_class, event_id, floors, weight, requires_condition, is_unique)`
Register an event class to the pool.

**Parameters:**
- `event_class` (Type): The Event class
- `event_id` (str): Unique identifier
- `floors` (str): Floor range. Options: 'early', 'mid', 'late', 'boss', 'all'
- `weight` (int): Selection weight. Default: 100
- `requires_condition` (Callable): Optional condition function. Default: None
- `is_unique` (bool): Whether event is unique. Default: False

#### `get_available_events(floor)`
Get all available events for current floor.

**Parameters:**
- `floor` (int): Current floor number

**Returns:** `List[EventMetadata]`

#### `get_random_event(floor)`
Get a random event weighted by their weights.

**Parameters:**
- `floor` (int): Current floor number

**Returns:** `Type` or `None`

#### `get_event_by_id(event_id)`
Get an event class by its ID.

**Parameters:**
- `event_id` (str): Event identifier

**Returns:** `Type` or `None`

#### `mark_event_used(event_id)`
Mark a unique event as used.

**Parameters:**
- `event_id` (str): Event identifier

#### `reset_unique_events()`
Reset all unique events for a new run.

## Examples

### Basic Event Registration

```python
@register_event(
    event_id="shrine_of_blood",
    floors='mid',
    weight=100
)
class ShrineOfBloodEvent(Event):
    def trigger(self) -> str:
        # Lose HP, gain gold
        self.action_queue.add_action(LoseHealthAction(amount=6))
        self.action_queue.add_action(AddGoldAction(amount=25))
        return None
```

### Unique Event

```python
@register_event(
    event_id="the_big_fish",
    floors='late',
    is_unique=True
)
class TheBigFishEvent(Event):
    def trigger(self) -> str:
        # Special reward event - only appears once
        self.action_queue.add_action(AddRelicAction(relic="GoldenAnchor"))
        return None
```

### Boss Floor Event

```python
@register_event(
    event_id="boss_reward",
    floors='boss',
    weight=200
)
class BossRewardEvent(Event):
    def trigger(self) -> str:
        # Special boss floor rewards
        self.action_queue.add_action(AddRandomRelicAction(
            rarities=[RarityType.RARE, RarityType.BOSS]
        ))
        return None
```

## Testing

The event pool system has comprehensive unit tests:

```bash
python -m unittest tests.test_event_pool -v
```

Tests cover:
- Event registration
- Floor pool assignment
- Event filtering by floor
- Unique event tracking
- Custom conditions
- Weighted random selection
- Event retrieval by ID

## Future Enhancements

Potential improvements:
1. Event dependencies (events that only appear after other events)
2. Event cooldowns (events that need time between appearances)
3. Event chains (events that lead to other events)
4. Dynamic weight adjustment based on game state
5. Event preview/hint system
6. Event probability debugging tools