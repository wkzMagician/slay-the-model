# ENGINE MODULE

## OVERVIEW
Core game engine managing game loop, global state, and combat system. All state is managed through singleton instances for consistency across game systems.

## ARCHITECTURE
```
engine/
├── game_flow.py      # Main game loop, room navigation
├── game_state.py     # Global state singleton, action queue
├── combat_state.py   # Combat mechanics, status effects
└── game_stats.py     # Static game constants
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Main game loop | `GameFlow.start_game()` | Room iteration, floor progression (0-16) |
| Room navigation | `GameFlow._select_next_room()` | AI vs Human mode selection logic |
| Global state access | `game_state` singleton | Import from `engine.game_state` |
| Action execution | `game_state.execute_all_actions()` | Central action queue processor |
| Combat state | `game_state.combat_state` | CombatState instance, phase tracking |
| Status effects | `game_state.combat_state.status_effects` | {entity_id: {effect: amount}} |
| Game phases | `game_state.game_phase` | "room", "map", "menu", "gameover" |
| Neo blessing stats | `game_stats` singleton | Character HP adjustments |

## CONVENTIONS

### Singleton Pattern
- **ALWAYS** import `game_state` from `engine.game_state` (never instantiate)
- **ALWAYS** use shared `game_state.action_queue` (ActionQueue from `actions.base`)
- Both `GameState` and `GameStats` are global singleton instances

### Action Queue Architecture
- Centralized queue: `game_state.action_queue.add_action()` to queue actions
- Execute via `game_state.execute_all_actions()` after queuing
- Supports both legacy string returns ("WIN", "DEATH") and new BaseResult types

### Combat System
- Three phases: "player_action", "enemy_action", "player_end"
- Status effects keyed by entity `id()` not string names
- Two-level reset: `reset_combat_info()` (per-combat) and `reset_turn_info()` (per-turn)
- Entity identity: use `id(entity)` as dictionary keys

### Room-Based Flow
- Main loop iterates rooms: `while current_floor < MAX_FLOOR (16)`
- Each room calls `.init()`, `.enter()`, `.leave()` lifecycle
- Rooms use global action queue, never create per-room queues
- Game ends when `enter()` returns "WIN" or "DEATH"

## ANTI-PATTERNS

**NEVER do these:**
- Instantiate `GameState` directly (use the singleton instance)
- Create per-room action queues (always use global `game_state.action_queue`)
- Skip `execute_all_actions()` after queueing actions (actions won't run)
- Reset status effects directly (use `apply_status()` and `reset_combat_info()`)
- Use string returns for new actions (return BaseResult from `utils.result_types`)
- Mix phase strings (only use "player_action", "enemy_action", "player_end")
- Access entity status without checking entity_id exists first

## NOTES

- **Backward compatibility**: `execute_all_actions()` handles legacy string returns alongside new BaseResult types
- **Event stack**: `game_state.event_stack` manages nested event contexts
- **Combat phase tracking**: `game_state.combat_state.current_phase` controls turn flow
- **Neow blessing**: Special room handled separately before main loop starts
