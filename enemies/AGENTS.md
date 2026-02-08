# ENEMIES SYSTEM KNOWLEDGE BASE

**Purpose:** Combat encounter definitions with stat-based enemy classes, organized by act.

## STRUCTURE
```
enemies/
├── __init__.py          # Exports all enemies
├── base.py              # Base Enemy class (inherits from Creature)
└── act1/                # Act 1 enemies
    ├── __init__.py      # Act 1 exports
    ├── cultist.py       # Common enemy
    ├── jaw_worm.py      # Common enemy
    ├── fungi_beast.py   # Elite enemy
    ├── louse_slaver.py  # Common enemy
    ├── the_guardian.py  # Boss (floor 3)
    ├── slime_boss.py    # Boss (floor 8)
    └── the_hexaghost.py # Final boss (floor 16)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Base enemy class | `base.py` | Enemy class inheriting from Creature |
| Enemy imports | `__init__.py` | Organized by act (act1/) |
| Act 1 enemies | `act1/` | All current enemies (7 total) |
| Damage calculation | `Enemy.take_damage()` | Handles weak, vulnerable, artifact |
| Creature base | `entities.creature.Creature` | HP, block, powers system |

## CONVENTIONS

### Enemy Class Definition
```python
from enemies.base import Enemy

class EnemyName(Enemy):
    """One-line docstring describing enemy type"""
    
    def __init__(self):
        super().__init__(
            name="Enemy Name",
            max_hp=XX,
            damage=YY,
            is_elite=False,  # or True
            is_boss=False    # or True
        )
```

### File Naming
- Snake case: `jaw_worm.py`, `the_guardian.py`
- Class names PascalCase matching name: `JawWorm`, `TheGuardian`
- Organized by act in subdirectories: `act1/`, `act2/`, etc.
- Boss names include "The": `TheGuardian`, `TheHexaghost`

### Act Organization
- Create new act subdirectories as needed: `act2/`, `act3/`, `act4/`
- Each act directory has its own `__init__.py`
- Main `enemies/__init__.py` imports from all act directories
- Example:
  ```
  enemies/
  ├── act1/  # Floors 0-16 (early game)
  ├── act2/  # Floors 17-32 (mid game)
  └── act3/  # Floors 33-48 (late game)
  ```

### Status Modifiers (inherited from Enemy)
- `strength`: Attack bonus (applied to damage output)
- `weak`: 25% damage reduction on incoming damage
- `vulnerable`: 50% extra damage taken
- `artifact`: Reduces debuff duration

## ANTI-PATTERNS

**NEVER do these:**
- Add AI behavior/patterns in enemy files (not implemented yet)
- Override `take_damage()` in individual enemies (use base class)
- Create complex `__init__()` logic beyond super().__init__()
- Add enemy-specific methods not in base Enemy class
- Import from `entities.enemy` (deprecated - use `enemies.base`)

**ALWAYS do these:**
- Import from `enemies.base.Enemy` (not `entities.enemy`)
- Keep enemy files simple (stat containers only)
- Set `is_elite=True` OR `is_boss=True` (mutually exclusive)
- Follow file naming convention: `the_boss_name.py` for "The Boss Name"
- Organize enemies by act in subdirectories

## PATTERNS

### Enemy Stats Scaling
- **Common**: HP 40-50, damage 6-10
- **Elite**: HP 80-90, damage 15-20
- **Boss**: HP 140-250, damage 25-35

### Boss Placement
- Floor 3: The Guardian (200 HP, 25 dmg) - Act 1
- Floor 8: Slime Boss (140 HP, 8 dmg) - Act 1
- Floor 16: The Hexaghost (250 HP, 35 dmg) - Act 1 (final boss)

### Adding New Enemies
1. Create file in appropriate act directory (e.g., `act2/new_enemy.py`)
2. Import from `enemies.base.Enemy`
3. Add to act's `__init__.py`
4. Add to main `enemies/__init__.py`
5. Update tests if needed

### Migration from Old Structure
- Old: `entities/enemy.py` → New: `enemies/base.py`
- Old: `entities/enemies.py` → New: `enemies/act1/` (split into individual files)
- Old imports: `from entities.enemy import Enemy` → New: `from enemies.base import Enemy`

## INHERITANCE HIERARCHY
```
Localizable (localization mixin)
    ↓
Creature (entities.creature.Creature)
    ↓
Enemy (enemies.base.Enemy)
    ↓
Specific Enemy Classes (Cultist, JawWorm, etc.)
```

### Creature Capabilities (inherited)
- HP management (`hp`, `max_hp` properties)
- Block system (`block` property, `gain_block()`)
- Damage system (`take_damage()` with power callbacks)
- Healing system (`heal()`)
- Power management (`add_power()`, `remove_power()`, `get_power()`)
- Death callback (`on_death()`)

### Enemy-Specific Additions
- Combat modifiers: `strength`, `weak`, `vulnerable`, `artifact`
- Enemy type flags: `is_elite`, `is_boss`
- Modified `take_damage()` with modifier applications
- `reset_for_combat()` for combat state reset