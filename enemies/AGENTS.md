# ENEMY SYSTEM - KNOWLEDGE BASE

## OVERVIEW
Act-based enemy definitions with intention AI system for turn-based combat.

## STRUCTURE
```
enemies/
├── base.py         # Enemy base class (HP, block, powers, damage/heal)
├── intention.py    # Intention system (AttackIntent, DefendIntent, etc.)
├── act1/          # Cultist, JawWorm, Slimes, Louse, FungiBeast
├── act2/          # Act 2 enemies
├── act3/          # Act 3 enemies
└── act4/          # SpireGrowth boss
```

## KEY CLASSES

| Symbol | Location | Role |
|--------|----------|------|
| `Enemy` | base.py | Base class with HP, block, power management |
| `Intention` | intention.py | Base intent class for AI actions |
| `AttackIntent` | intention.py | Deal damage to player |
| `DefendIntent` | intention.py | Gain block |
| `BuffIntent` | intention.py | Apply buffs to self |
| `DebuffIntent` | intention.py | Apply debuffs to player |
| `SleepIntent` | intention.py | Skip turn |
| `@register` | utils/registry.py | Auto-register enemies to global lookup |

## INTENTION SYSTEM

Enemies define behavior via Intention objects:
- `create_intention()`: Returns next turn's Intention based on AI logic
- `take_turn()`: Executes current Intention (deal damage, gain block, apply power)
- Intentions can be deterministic (pattern) or random

## ADDING ENEMIES

1. Create file in appropriate act directory: `enemies/act{1-4}/{enemy_name}.py`
2. Inherit from Enemy, set HP, block values
3. Define `create_intention()` method with AI logic
4. Add `@register` decorator (auto-registers to registry)
5. Add localization JSON entries

## ANTI-PATTERNS

- **NO** skipping @register decorator - enemies won't load
- **NO** direct HP manipulation - use `damage()` or `heal()` methods
- **NO** hardcoded player references in intentions - use current combat state
- **NO** modifying Enemy base class unless extending functionality
