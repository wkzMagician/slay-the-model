# SLAY THE MODEL - KNOWLEDGE BASE

**Generated:** 2026-02-20
**Commit:** ef19e04
**Branch:** main

## OVERVIEW

Python roguelike deck-builder (Slay the Spire clone). Turn-based combat with cards, enemies, relics, potions. No UI - CLI/game logic only.

## STRUCTURE

```
.
├── __main__.py          # Entry: imports cards.ironclad, potions, powers, relics → starts GameFlow
├── engine/              # Core game loop, state management, combat resolution
├── actions/             # Global ActionQueue, delayed actions, action resolution
├── cards/               # Card definitions (base.py, ironclad/, colorless/), @register decorator
├── enemies/             # Enemy definitions by act (act1/, act2/, act3/, act4/), intention system
├── powers/              # Power/buff/debuff definitions, @register decorator
├── player/              # PlayerManager, player state management
├── rooms/               # Room types: Combat, Rest, Shop, Treasure, Event, Neo
├── events/              # 60+ random events with choices and outcomes
├── potions/             # Potion definitions and effects
├── relics/              # Relic definitions and triggers
├── utils/               # Registry, localizable base, type definitions
├── config/              # YAML configs (game_config.yaml has god_mode debug)
├── localization/        # i18n: en/, zh/
└── tests/               # 668 tests, CombatTestHelper utility
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add new card | `cards/ironclad/` or `cards/colorless/` | Use @register decorator, inherit Card |
| Add new enemy | `enemies/act{1-4}/` | Inherit Enemy, define intentions |
| Add new power | `powers/` | Use @register decorator, inherit Power |
| Add new event | `events/` | Inherit Event, define choices |
| Modify combat flow | `engine/combat.py` or `engine/combat_state.py` | |
| Change game state | `engine/game_state.py` | Singleton pattern |
| Add new room type | `rooms/` | Inherit Room base |
| Debug/testing | `tests/test_combat_utils.py` | CombatTestHelper class |
| Localization | `localization/{en,zh}/` | JSON files |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `GameFlow` | class | `engine/game_flow.py` | Main game loop controller |
| `GameState` | class | `engine/game_state.py` | Singleton game state |
| `ActionQueue` | class | `actions/action_queue.py` | Global action resolution |
| `Card` | class | `cards/base.py` | Base card class |
| `Enemy` | class | `enemies/base.py` | Base enemy class |
| `Intention` | class | `enemies/intention.py` | Enemy AI intent system |
| `Power` | class | `powers/base.py` | Base power class |
| `Room` | class | `rooms/base.py` | Base room class |
| `CombatTestHelper` | class | `tests/test_combat_utils.py` | Test utility for combat |
| `@register` | decorator | `utils/registry.py` | Registry pattern for cards/enemies/powers |
| `Localizable` | class | `utils/localizable.py` | Localization support base |

## CONVENTIONS

**Style:** Google Python Style Guide. 79 char lines, 4-space indent.

**Naming:**
- Modules: `lower_with_under`
- Classes: `CapWords`
- Functions/vars: `lower_with_under`
- Constants: `CAPS_WITH_UNDER`
- Private: `_prefix`

**Imports:** stdlib → third-party → local. Use `TYPE_CHECKING` for forward refs.

**Registry:** Use `@register` decorator for cards/enemies/powers. Auto-registers to global lookup.

**Localization:** Inherit `Localizable`, set `localization_prefix`, add JSON to `localization/{en,zh}/`.

## ANTI-PATTERNS

- **NO** direct GameState instantiation - use singleton accessor
- **NO** circular imports - use lazy imports or TYPE_CHECKING
- **NO** hardcoded strings for display - use localization system
- **NO** modifying ActionQueue directly during resolution - queue actions instead

## COMMANDS

```bash
# Run game
python __main__.py

# Run tests
pytest tests/
python -m unittest discover tests/
python run_game_test.py

# PowerShell runner
pwsh run_games.ps1
```

## NOTES

- No requirements.txt/pyproject.toml - dependencies not tracked
- No linting config (ruff, flake8, mypy) present
- `config/game_config.yaml` has `god_mode` for debug
- `run_game_test.py` runs automated game simulations
