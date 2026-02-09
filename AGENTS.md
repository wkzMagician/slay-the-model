# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-09T02:53:33Z
**Commit:** 2a9687a
**Branch:** main

## OVERVIEW
Python deck-building roguelike (117 Python files, 13,876 lines, 20 game systems). NOT a proper package - direct execution only.

## STRUCTURE
```
slay-the-model/
├── actions/      # Game actions (10 files)
├── ai/           # AI modules (2 files)
├── ai_tools/      # AI utilities (2 files)
├── cards/        # Card definitions by character (Ironclad only, 2 files)
├── config/       # Game configuration (YAML)
├── enemies/       # Enemy definitions (3 files + act1/ subdirectory)
├── engine/        # Core engine (GameFlow, GameState, CombatState, 5 files)
├── entities/      # Base classes (Card, Enemy, Player, 3 files)
├── events/        # Random events (10 files)
├── localization/  # i18n (en.yaml, zh.yaml, 1 file)
├── logs/          # Debug log output
├── map/          # Map generation & placement (5 files)
├── orbs/         # Orb mechanics (1 file)
├── player/        # Player character classes (6 files)
├── potions/       # Potions (7 files)
├── powers/        # Status effects (2 files)
├── relics/        # Relics (global + character, 2 files)
├── rooms/         # Room types (8 files)
├── tests/         # 113 tests (pytest + unittest hybrid, 17 files)
└── utils/         # Utilities (5 files)
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

**Critical Architectural Patterns:**
- Action Execution: All actions/events/rooms inherit from `actions.base.ActionQueue`
- Actions return `ResultType` from `utils.result_types.BaseResult`
- Game state processes actions via `game_state.execute_all_actions()`
- Single `game_state` singleton manages ALL persistent data

**Localization System:**
- Template-based i18n with `{variable}` placeholders
- Runtime loading via `localization/` (en.yaml, zh.yaml)
- Apply via `localize()` helper function

**Game Loop:**
- Floors 0-16 (MAX_FLOOR constant)
- Per floor: map generation → enter rooms → events → rest
- Victory: Floor 16 with no DEATH event
- Defeat: HP ≤ 0 OR 3 DEATH events

**Return Types (from `utils/result_types.py`):**
- `BaseResult`: Base class for all actions
- `SingleActionResult`: One ResultType + next room/event
- `MultipleActionsResult`: Queue multiple actions for same turn
- `GameStateResult`: Win/Death/end-game
- `NoneResult`: No state change

**Development Standards:**
- **Entry Point:** `__main__.py` creates GameFlow, starts game loop, handles KeyboardInterrupt, TeeStream logging
- **Dependencies:** NO `requirements.txt`/`pyproject.toml` - manual installation, direct execution via `python __main__.py`
- **Code Style (Google Python Style Guide):** `import package` for libs, `from package import module` for internals, 80-char limit, `ALL_CAPS` constants, `_leading_underscore` for internal modules

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
