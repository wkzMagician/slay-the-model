# POTIONS SYSTEM KNOWLEDGE BASE

## OVERVIEW
Consumable items with instant effects, organized by rarity and character specificity.

## STRUCTURE
```
potions/
├── base.py              # Potion base class
├── global_potions.py     # All potion definitions (577 lines)
└── [character]_potions.py # Character-specific potions (e.g., ironclad_potions.py)
```

## WHERE TO LOOK
| Task | File | Notes |
|------|-------|-------|
| Potion base class | `base.py` | Potion parent class with rarity and effect |
| All potions | `global_potions.py` | 20+ potion definitions |
| Ironclad potions | `ironclad_potions.py` | Warrior-specific potions |

## POTION RARITIES

**Rarity Types:**
- **COMMON**: Basic potions (Block Potion, Strength Potion, etc.)
- **UNCOMMON**: Moderate effects (Explosive Potion, Fire Potion)
- **RARE**: Powerful effects (Fairy Potion, Gamble Potion)

**Effects:**
- Direct: heal, block, gain energy, draw cards
- Combat: damage, apply debuffs (weak, vulnerable)
- Utility: card manipulation, random effects

## CONVENTIONS

**Potion Definition:**
```python
class PotionName(Potion):
    def __init__(self):
        super().__init__(
            name="Potion Name",
            rarity=RarityType.COMMON,
            effect=lambda: self._apply_effect()
        )
```

**Usage Pattern:**
- Potions added via `AddRandomPotionAction`
- Used in combat via `UsePotionAction`
- One-time consumables (removed after use)
- Shop sells 3 potions per rest site

## ANTI-PATTERNS

**NEVER:**
- Add execution logic to potion classes (keep data-only)
- Create potions without rarity
- Skip effect lambda (required for deferred execution)

**ALWAYS:**
- Import from `potions.base.Potion`
- Use `RarityType` from `utils.types`
- Keep potion files < 30 lines (data-only)
