# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-07T12:33:51Z
**Commit:** ea66759
**Branch:** main

## OVERVIEW
Python deck-building roguelike "Slay the Spire" clone with 100+ files across 20+ game systems.

## STRUCTURE
```
slay-the-model/
├── actions/      # Game actions (card play, combat, reward, room transitions)
├── cards/        # Card definitions by character (Ironclad only)
├── config/       # Game configuration (YAML)
├── enemies/       # Enemy definitions
├── engine/        # Core engine (GameFlow, GameState, CombatState)
├── entities/      # Base classes (Card, Enemy, Player)
├── events/        # Random events
├── localization/  # i18n (en.yaml, zh.yaml)
├── map/          # Map generation & placement
├── orbs/         # Orb mechanics
├── player/        # Player character classes
├── potions/       # Potions
├── powers/        # Status effects (poison, vulnerable, etc.)
├── relics/        # Relics (global + Ironclad)
├── rooms/         # Room types (monster, elite, boss, rest, merchant)
├── utils/         # Utilities (ResultTypes, localization helpers)
└── tests/         # 113 tests (pytest + unittest hybrid)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Main entry point | `__main__.py` | Creates GameFlow, starts game loop |
| Game configuration | `config/game_config.yaml` | Mode (human/ai), language (en/zh), debug settings |
| Localization | `localization/en.yaml`, `localization/zh.yaml` | Template-based i18n with `{variable}` placeholders |
| Card definitions | `cards/ironclad/` | 22 card files (name, description, upgrades) |
| Enemy definitions | `enemies/` | Enemy classes and behaviors |
| Room definitions | `rooms/` | 7 room type modules |
| Event system | `events/` | Event pool and individual events |
| Action classes | `actions/` | 13 action modules (combat, reward, display) |
| Game engine | `engine/` | GameFlow (main loop), GameState (singleton), CombatState |
| Relic system | `relics/` | Global relics + Ironclad-specific (22 files total) |
| Player classes | `player/` | Player character implementation |
| Test files | `tests/` | Mixed pytest/unittest, 113 tests |

## CONVENTIONS

### Critical Architectural Patterns

**Action Execution Flow:**
1. All actions/events/rooms inherit from `actions.base.ActionQueue`
2. Actions return `ResultType` from `utils.result_types.BaseResult`
3. Game state processes actions via `game_state.execute_all_actions()`
4. Single `game_state` singleton instance manages ALL persistent data

**Localization System:**
- Use `{variable}` placeholders in YAML templates
- Load at runtime via `localization/`
- Both English (`en.yaml`) and Chinese (`zh.yaml`) supported
- Apply via `localize()` helper function

**Game Loop:**
- Floors 0-16 (MAX_FLOOR constant)
- Each floor: map generation → enter rooms → events → rest
- Victory: Floor 16 with no DEATH event triggered
- Defeat: Player HP ≤ 0 (any time) or 3 DEATH events

**Return Types (from `utils/result_types.py`):**
- `BaseResult`: Base class for all actions
- `SingleActionResult`: Returns one ResultType + next room/event
- `MultipleActionsResult`: Queues multiple actions for same turn
- `GameStateResult`: Win/Death/end-game
- `NoneResult`: No state change (e.g., invalid card play)

### Development Standards

**Entry Point:**
- `__main__.py` imports `GameFlow` from `engine.game_flow`
- Creates global `game_state` singleton on module import
- Handles KeyboardInterrupt with localized messages
- TeeStream logging (duplicates stdout to both console AND `logs/debug.log`)

**Dependencies:**
- **CRITICAL**: No `requirements.txt`, `pyproject.toml`, or dependency tracking
- Direct module imports only (no formal packaging)
- Install dependencies manually, run via `python -m slay-the-model`

**Code Style (per `pyguide.md` - Google Python Style Guide):**
- Imports: `import package` for libraries, `from package import module` for internals
- Type annotations recommended for public APIs
- 80-char line limit
- Constants: `ALL_CAPS_WITH_UNDERSCORES`
- Internal modules: `_leading_underscore`

### Anti-Patterns (THIS PROJECT)

**NEVER do these:**
- Add `requirements.txt`, `pyproject.toml`, or any dependency management
- Modify `engine.game_state` import pattern (singleton is intentional)
- Remove debug logging from `__main__.py` (essential for game development)
- Break `game_state` singleton (it's intentional for game design)

**ALWAYS do these:**
- Return `ResultType` from actions (not strings like "WIN"/"DEATH")
- Load config from `config/game_config.yaml` at startup
- Use `localize()` for all user-facing text
- Inherit from `ActionQueue` when creating new actions
- Import from `engine.game_state` (not create new instances)

**Deprecated Patterns (avoid or replace):**
- Legacy return strings: "WIN", "DEATH", "LOSE" → use `ResultType.VICTORY`, `ResultType.DEATH`
- `cards/ironclad/` hardcoded character class → parameterize
- Direct English strings in code → use localization system

## COMMANDS

```bash
# Run the game
python __main__.py

# Run tests (pytest - installed)
python -m pytest tests/ -v

# Run specific test (unittest)
python tests/test_enemies.py

# Run specific test (pytest)
python -m pytest tests/test_rooms.py -v

# Enable debug mode (logs to logs/debug.log)
python __main__.py --debug
```

## NOTES

### Project Status
- **Work-in-progress prototype**: Not a proper Python package (no `pyproject.toml`)
- **Direct execution only**: Must run from source directory or use `python -m slay-the-model` (only works if installed)
- **No CI/CD**: Manual testing only
- **Hybrid test framework**: Both pytest (recommended) and unittest (legacy) in 113 test files
- **Dependency hell risk**: New developers cannot reproduce environment without manual setup

### Gotchas
- **Circular import issue in tests**: `tests/test_events.py` uses `importlib.util` to load `events.event_pool` because direct imports would cause circular dependency between `engine.game_state` and `rooms.neo`. This is intentional workaround, not a bug.
- **PyInstaller artifacts**: `.gitignore` mentions `*.spec` and `*.manifest` suggesting PyInstaller was used at some point, but no build configuration exists.
- **Config loading**: Assumes project structure relative to `engine/` directory (hardcoded path in `config/game_config.py`). Breaking directory structure breaks config loading.
- **Debug logging default**: Debug mode is ON by default (writes to `logs/debug.log`). This is intentional for game development but may confuse players.

### Architecture Notes
- **Global state singleton**: `engine.game_state.game_state` is imported at module level (line 56) and shared globally. This makes testing harder but ensures consistent game state across all systems.
- **Action queue pattern**: All actions flow through centralized queue in `game_state.execute_all_actions()`.
- **Localization system**: Template-based with runtime variable substitution, supports English/Chinese.
- **Character-specific directories**: Ironclad relics/cards/powers have own subdirs (`relics/ironclad/`, `cards/ironclad/`, `powers/ironclad/`) - pattern for adding new characters.

## UNIQUE STYLES

### Game Design
- **Deck-building roguelike**: Battle cards with energy costs, strategic card management
- **16-floor progression**: Linear dungeon crawl with boss fights at floors 3, 8, 11, 15
- **Relic system**: Global relics (available to all characters) + character-specific relics
- **Event system**: Random encounters between rooms (Neo shrine, chest, elite fights, etc.)
- **Rest mechanics**: Heal, upgrade cards, remove cards at rest sites

### Code Organization
- **Domain-driven directories**: Each game domain has its own directory (actions, cards, enemies, rooms, etc.)
- **No root __init__.py**: Project is a module, not a package
- **Explicit imports**: Use full package paths (`from slay_the_model.engine.game_state import game_state`)
- **Result type system**: Centralized in `utils.result_types` with base classes

### Localization Style
- **Variable substitution**: `{card_name}`, `{enemy_name}`, `{amount}` placeholders
- **YAML structure**: Key-value pairs with nested objects
- **Bilingual**: English default, Chinese optional via `--language zh` flag
