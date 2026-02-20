# CARDS - CARD SYSTEM

**Generated:** 2026-02-20
**Commit:** ef19e04
**Branch:** main

## OVERVIEW

Deck-building card system with character-specific and colorless cards using registry pattern.

## STRUCTURE

```
cards/
├── base.py          # Card base class with play(), upgrade(), clone()
├── ironclad/        # Ironclad-specific cards (~50+ cards)
└── colorless/        # Colorless cards available to all characters
```

## KEY CLASSES

| Class | Location | Role |
|-------|----------|------|
| `Card` | `base.py` | Base class with cost, type, target, exhaust, innate |
| `@register` | `utils/registry.py` | Decorator auto-registers cards to namespace |

## ADDING CARDS

| Character | Location | Example |
|-----------|----------|----------|
| Ironclad | `cards/ironclad/{card_name}.py` | `cards/ironclad/strike.py` |
| Colorless | `cards/colorless/{card_name}.py` | `cards/colorless/crash.py` |

**Card Template:**
```python
from cards.base import Card, CardType
from utils.registry import register

@register('ironclad.strike')
class Strike(Card):
    def __init__(self):
        super().__init__(cost=1, type=CardType.ATTACK, target=Target.ENEMY)
```

**Card.play()** returns `Action` or `list[Action]` for combat resolution.

## ANTI-PATTERNS

- **NO** skipping @register decorator - cards won't be discoverable
- **NO** direct card instantiation in combat - use card pool/draw pile
- **NO** modifying cost directly - use cost modifiers/relics instead
- **NO** hardcoding target in play() - respect target type from init
