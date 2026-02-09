# UTILITIES DIRECTORY KNOWLEDGE BASE

## OVERVIEW
Cross-cutting utilities and helper functions used throughout the project (5 files, 482 lines).

## STRUCTURE
```
utils/
├── result_types.py     # BaseResult, ResultType enums, action return types
├── localization.py     # i18n helper with variable substitution
└── [other utils]       # Various helper functions
```

## WHERE TO LOOK
| Task | File | Notes |
|------|-------|-------|
| Result types | `result_types.py` | BaseResult, SingleActionResult, MultipleActionsResult, GameStateResult |
| Localization | `localization.py` | `localize()` function, template substitution |
| Type definitions | Various files | RarityType, CardType, etc. |

## CORE UTILITIES

**Result Types (result_types.py):**
```python
# Return types from actions
class ResultType(Enum):
    NONE = 0
    VICTORY = 1
    DEATH = 2
    MENU = 3

class BaseResult:
    """Base for all action results"""

class SingleActionResult(BaseResult):
    """Returns one action + next room/event"""

class MultipleActionsResult(BaseResult):
    """Queue multiple actions for same turn"""

class GameStateResult(BaseResult):
    """Game ending (WIN/DEATH/end-game)"""

class NoneResult(BaseResult):
    """No state change (e.g., invalid card play)"""
```

**Localization (localization.py):**
- Loads YAML files from `localization/`
- Substitutes `{variable}` placeholders at runtime
- Supports en.yaml, zh.yaml

## CONVENTIONS

**Result Type Usage:**
- Actions MUST return `BaseResult` subclass
- Use `NoneResult()` for no-op actions
- Use `SingleActionResult(action)` to queue next action
- Use `MultipleActionsResult([actions])` for batch actions
- Use `GameStateResult(ResultType.VICTORY/DEATH)` for game ending

**Localization:**
- `localize(key, **kwargs)` returns localized text
- All user-facing text must use `localize()`
- Keys follow pattern: `domain.action.variable` (e.g., `rooms.combat.enter`)

**Import Patterns:**
- `from utils.result_types import *` for ResultType
- `from utils.localization import localize` for i18n

## ANTI-PATTERNS

**NEVER:**
- Return strings ("WIN"/"DEATH") from actions → use ResultType
- Return `None` instead of `NoneResult()`
- Hardcode English strings → use `localize()`
- Mix synchronous/async result handling

**ALWAYS:**
- Return BaseResult subclass from actions
- Import ResultType from utils.result_types
- Use `localize()` for all user-facing text
- Use variable substitution for dynamic values (`{amount}`, `{card_name}`)

## CROSS-DOMAIN USAGE

**utils/result_types** is imported by:
- All action classes
- All room classes
- All event classes
- Game engine (GameFlow, GameState)

**utils/localization** is imported by:
- Localizable classes (actions, rooms, events)
- Player display methods
- Enemy descriptions
