# EVENTS DOMAIN KNOWLEDGE

## OVERVIEW
Random encounters that occur in Unknown Rooms. Events offer player choices with rewards/punishments.

## STRUCTURE
```
events/
├── base_event.py       # Event and CombatEvent base classes
├── event_pool.py       # Centralized registry and weighted selection
├── neo_event.py        # Special starting event (Neow blessing)
├── big_fish.py        # Simple choice event example
├── the_cleric.py      # Random relic encounter
├── house_of_god.py    # Divine relic selection
├── the_shrine.py      # HP sacrifice/gold/heal choices
├── woman_in_blue.py    # Mid-game rare card/gold encounter
└── __init__.py        # Imports all events for auto-registration
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Base event classes | `base_event.py` | Event, CombatEvent, trigger() signature |
| Event registration | `event_pool.py` | @register_event decorator, EventPool class |
| Simple choice event | `big_fish.py` | Minimal event with SelectAction + Option |
| Event with conditions | `neo_event.py` | Checks game state before showing options |
| Weighted selection logic | `event_pool.py:124-147` | get_random_event() weighted by weights |
| Floor range logic | `event_pool.py:172-189` | early(1-4), mid(5-10), late(11-15), boss(16) |

## CONVENTIONS

### Event Registration Pattern
```python
@register_event(
    event_id="unique_id",
    floors='early',  # 'early', 'mid', 'late', 'boss', 'all'
    weight=100,      # Higher = more likely
    is_unique=False   # True = once per run
)
class MyEvent(Event):
    def trigger(self) -> BaseResult:
        ...
```

### Event Flow Pattern
1. Create actions list to collect all actions
2. Add `DisplayTextAction` to actions list (optional)
3. Build `Option` list with actions to execute
4. Add `SelectAction` to actions list (title + options)
5. Call `self.end_event()` to mark complete (if applicable)
6. Return `MultipleActionsResult(actions)` or `SingleActionResult(action)`

### Action Queue Usage
Events should NOT directly call `game_state.action_queue.add_action()`. Instead, collect all actions in a list and return them via `MultipleActionsResult(actions)`. The GameFlow will handle execution.

## ANTI-PATTERNS

**NEVER do these:**
- Return strings ("WIN", "DEATH") from trigger() → use ResultType
- Directly modify game state without actions → use action queue
- Call `game_state.action_queue.add_action()` or `execute_all_actions()` inside trigger() → return MultipleActionsResult instead
- Import event files directly in tests → use `event_pool.get_event_by_id()`

**ALWAYS do these:**
- Inherit from `Event` (or `CombatEvent` for combat events)
- Register events in `__init__.py` imports for auto-registration
- Use `Option` objects with `actions` list for player choices
- Check `game_state.run_history` for conditional options (like NeoEvent)

## FLOOR RANGES
- `early`: Floors 1-4 (basic encounters)
- `mid`: Floors 5-10 (more complex events)
- `late`: Floors 11-15 (high-stakes choices)
- `boss`: Floor 16 (unique boss events)
- `all`: Any floor (generic events)
