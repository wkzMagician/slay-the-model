# ACTIONS MODULE - GLOBAL ACTION QUEUE

Global action queue system for sequential combat resolution.

## KEY CLASSES

| Class | Location | Role |
|-------|----------|------|
| `ActionQueue` | `action_queue.py` | Global queue for sequential action resolution |
| `Action` | `base.py` | Base class for all action types |
| `AttackAction` | Various | Deal damage to target |
| `DefendAction` | Various | Gain block amount |
| `ApplyPowerAction` | Various | Add power/buff/debuff to entity |
| `DrawCardAction` | Various | Draw cards from deck |
| `GainEnergyAction` | Various | Modify player energy |

## PATTERNS

- **Queue-then-resolve**: Actions added to global ActionQueue, resolved sequentially
- **execute() method**: Each action type implements execute() to perform effect
- **Chain reactions**: Actions can spawn additional actions during execution
- **Global access**: ActionQueue accessible via GameState singleton
- **Delayed effects**: Use AddToBotAction for end-of-turn effects

## ANTI-PATTERNS

- **NO** modifying ActionQueue during action resolution - queue instead
- **NO** direct effect application without using action system
- **NO** skipping queue for "instant" effects - everything goes through queue
- **NO** executing actions directly - always push to ActionQueue
