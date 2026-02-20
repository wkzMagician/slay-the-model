# UTILS - SHARED UTILITIES

Shared utilities and base classes. Registry decorator, localization base, type definitions, logging.

## KEY CLASSES

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `Localizable` | class | `localizable.py` | Base class for i18n support |
| `GameLogger` | class | `game_logger.py` | Centralized logging utilities |

## REGISTRY

Use `@register` decorator to auto-register classes to global lookup.

```python
from utils.registry import register

@register
class MyCard(Card):
    pass  # Auto-registered
```

Auto-registers cards/enemies/powers to global lookup. No manual registration needed.

## LOCALIZATION

Inherit `Localizable` for i18n support. Set `localization_prefix`.

```python
class MyCard(Card, Localizable):
    localization_prefix = "cards.my_card"
    # Looks up in localization/{en,zh}/cards.json
```

All display text goes through localization system.

## ANTI-PATTERNS

- **NO** manual registration - use @register decorator
- **NO** hardcoded strings for display - use Localizable
