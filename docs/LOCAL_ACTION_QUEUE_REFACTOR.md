# Local Action Queue Refactoring

## Overview

Previously, the game architecture used a **global `action_queue`** that was shared across all rooms, events, and combat. This created several issues:

- Tight coupling between different game contexts
- Difficult to manage action isolation
- Actions from one context could interfere with another

The refactoring moves to **local `action_queue` instances** for each Room, Event, and Combat, providing better separation and cleaner architecture.

## Changes Made

### 1. Removed Global Action Queue

**File: `actions/base.py`**
- Removed the global `action_queue` instance
- Only `ActionQueue` class remains for creating local instances

**File: `actions/__init__.py`**
- Removed `action_queue` from exports
- Updated module documentation to reflect new architecture

### 2. Combat Uses Local Action Queue

**File: `engine/combat.py`**
- Changed from: `self.action_queue = action_queue`
- Changed to: `self.action_queue = ActionQueue()`
- Combat now has its own isolated action queue

### 3. Actions Return Actions Instead of Adding to Queue

Instead of actions directly adding themselves to a global queue, they now return other actions which the caller adds to its local queue.

**Files Modified:**

#### `actions/treasure.py`
- Removed import of `action_queue`
- `OpenChestAction` now returns `SelectAction` instead of adding to global queue
- Caller (TreasureRoom) handles adding returned actions to its queue

#### `actions/card.py`
- Removed all `from actions import action_queue` imports
- Modified actions to return actions instead of adding to queue:
  - `TransformCardAction`: Returns list of actions
  - `ChooseRemoveCardAction`: Returns `SelectAction`
  - `ChooseTransformCardAction`: Returns `SelectAction`
  - `ChooseUpgradeCardAction`: Returns `SelectAction`
  - `ChooseAddRandomCardAction`: Returns `SelectAction`
  - `AddRandomCardAction`: Returns `AddCardAction`

#### `actions/map_selection.py`
- Removed `from actions.base import action_queue` imports
- `SelectMapNodeAction._make_human_decision()`: Returns `SelectAction`
- `SelectMapNodeAction._execute_move_via_action()`: Returns `MoveToMapNodeAction`

### 4. Room.execute_actions() Handles Returned Actions

**File: `rooms/base.py`**
- Updated `execute_actions()` to handle actions that return other actions
- Automatically adds returned actions to the front of the queue
- Handles both single actions and lists of actions
- Maintains existing behavior for special return values ("DEATH", "WIN")

**Example:**
```python
def execute_actions(self) -> str:
    while not self.should_leave and not self.action_queue.is_empty():
        result = self.action_queue.execute_next()
        
        # Check if action returned another action to add to queue
        if result is not None:
            if isinstance(result, list):
                # Add list of actions to front of queue
                self.action_queue.add_actions(result, to_front=True)
            elif isinstance(result, Action):
                # Add single action to front of queue
                self.action_queue.add_action(result, to_front=True)
            elif result in ("DEATH", "WIN"):
                return result
    
    return None
```

### 5. TreasureRoom Updated

**File: `rooms/treasure.py`**
- Added custom `execute_actions()` method
- Handles `OpenChestAction` returning `SelectAction` for boss chests
- Automatically adds returned `SelectAction` to queue

## Architecture Benefits

### 1. Isolation
- Each Room has its own action queue
- Each Event has its own action queue
- Combat has its own action queue
- No cross-contamination between contexts

### 2. Clear Ownership
- Actions are clearly owned by their creating context
- No global state to worry about
- Easier to reason about action flow

### 3. Flexibility
- Actions can return new actions dynamically
- Callers control when/how to add returned actions
- Supports complex action chains and dependencies

### 4. Testability
- Easier to test individual components
- Can create isolated action queues for testing
- No global state to reset between tests

## Migration Guide

### For New Actions

**Old Way (Global Queue):**
```python
from actions import action_queue

class MyAction(Action):
    def execute(self):
        # Do something
        action_queue.add_action(AnotherAction())
```

**New Way (Return Actions):**
```python
class MyAction(Action):
    def execute(self):
        # Do something
        return AnotherAction()  # Caller will add to their queue
```

### For Rooms

Rooms don't need changes - they already have `self.action_queue`. The base `Room.execute_actions()` now handles returned actions automatically.

**Custom execute_actions (if overriding):**
```python
def execute_actions(self) -> str:
    while not self.should_leave and not self.action_queue.is_empty():
        result = self.action_queue.execute_next()
        
        # Handle returned actions
        if result and isinstance(result, Action):
            self.action_queue.add_action(result, to_front=True)
        
        # Handle special return values
        if result in ("DEATH", "WIN"):
            return result
    
    return None
```

## Compatibility Notes

- **Existing Rooms**: No changes needed unless they have custom `execute_actions()`
- **Existing Events**: No changes needed
- **Existing Actions**: Need to be updated if they use `action_queue.add_action()`
- **Tests**: Need to ensure they create their own action queues instead of using global

## Future Considerations

### Action Chaining
This pattern enables sophisticated action chaining:

```python
class ComplexAction(Action):
    def execute(self):
        # Return list of actions to execute in sequence
        return [
            Action1(),
            Action2(),
            Action3(),
        ]
```

### Conditional Actions
Actions can return different actions based on conditions:

```python
class ConditionalAction(Action):
    def execute(self):
        if some_condition:
            return RewardAction()
        else:
            return PenaltyAction()
```

### Nested Actions
Actions can return actions that themselves return actions:

```python
class OuterAction(Action):
    def execute(self):
        return InnerAction()

class InnerAction(Action):
    def execute(self):
        return FinalAction()
```

All returned actions are automatically added to the caller's queue and executed in order.