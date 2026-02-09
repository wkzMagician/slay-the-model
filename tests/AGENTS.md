# TESTS DIRECTORY KNOWLEDGE BASE

## OVERVIEW
Hybrid test framework (pytest + unittest) covering all game systems with 113 tests.

## TEST STRUCTURE
```
tests/
├── test_*.py              # Individual test files (17 total)
└── __pycache__/          # Test bytecode
```

## TEST FRAMEWORK

**Hybrid Approach:**
- pytest for test discovery (`python -m pytest tests/ -v`)
- unittest-style test classes (inherit from `unittest.TestCase`)
- No centralized test config (no `pytest.ini`, `conftest.py`)

**Running Tests:**
```bash
# All tests
python -m pytest tests/ -v

# Specific file (pytest)
python -m pytest tests/test_rooms.py -v

# Specific file (unittest)
python tests/test_enemies.py
```

## CONVENTIONS

**Test Organization:**
- One test class per file for related functionality
- Test methods start with `test_`
- Use `unittest.TestCase` base class
- Mock game_state singleton for isolation

**Circular Import Workaround:**
- `test_events.py` uses `importlib.util` to load `events.event_pool`
- Avoids circular dependency between `engine.game_state` and `rooms.neo`

## ANTI-PATTERNS

**NEVER:**
- Add `pytest.ini` or `conftest.py` (no centralized config exists)
- Create per-package test directories (keep all in tests/)
- Mix pytest fixtures and unittest.TestCase patterns

**ALWAYS:**
- Inherit from `unittest.TestCase`
- Use descriptive test method names (`test_card_play_reduces_energy`)
- Mock `game_state` for isolation when needed

## DOMAIN-SPECIFIC NOTES

**Test Coverage:**
- Actions: combat, card, reward, display
- Rooms: combat, rest, shop, treasure
- Events: event pool selection
- Map: map generation, encounter pool
- Engine: game flow, combat state
- Entities: creature, enemy, player
- Cards: ironclad cards
- Potions: global potions
- Relics: global + ironclad relics
