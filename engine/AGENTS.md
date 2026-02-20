# ENGINE - CORE GAME ENGINE

**Generated:** 2026-02-20
**Commit:** ef19e04
**Branch:** main

## OVERVIEW

Core game loop, state management, combat resolution, and player input handling.

## KEY CLASSES

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `GameFlow` | class | `game_flow.py` | Main game loop controller, orchestrates room transitions, combat, rewards |
| `GameState` | class | `game_state.py` | Singleton game state, stores all persistent game data |
| `Combat` | class | `combat.py` | Combat resolution system, turn management, damage calculation |
| `CombatState` | class | `combat_state.py` | Combat-specific state, battle-only data (turn, intentions) |
| `PlayerChoice` | class | `player_choice.py` | Player input handling, choice resolution |

## PATTERNS

**Singleton Access:** Always use `GameState.getInstance()` - never call `GameState()` directly.

**Flow Control:** GameFlow drives all room transitions, combat start/end, and reward distribution.

**State Separation:** CombatState handles battle-specific data (turn count, enemy intentions), while GameState holds persistent data.

**Input Handling:** PlayerChoice validates and resolves player decisions through GameFlow.

## ANTI-PATTERNS

- **NO** direct GameState() instantiation - always use singleton accessor
- **NO** bypassing GameFlow for game progression or room changes
- **NO** storing state outside GameState singleton
- **NO** direct CombatState modifications during game flow
