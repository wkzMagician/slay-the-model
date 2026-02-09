# ACTIONS DIRECTORY KNOWLEDGE BASE

## OVERVIEW
All game mechanics flow through action classes that inherit from `actions.base.Action`.
Actions return `ResultType` from `utils.result_types` to drive game flow.

## ACTION CLASS PATTERN

```python
@register("action")
class MyAction(Action):
    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        # Action logic
        return NoneResult()
```

**ResultType Returns:**
- `NoneResult()`: Action completed, no follow-up
- `SingleActionResult(action)`: Queue one action next
- `MultipleActionsResult([actions])`: Queue multiple actions
- `GameStateResult`: Win/Death/end-game transition

## WHERE TO LOOK

| Task | File | Key Actions |
|------|-------|-------------|
| Damage/block/status | `combat.py` | DealDamageAction, GainBlockAction |
| Card play/energy | `combat.py` | PlayCardAction, GainEnergyAction, EndTurnAction |
| Card manipulation | `card.py` | AddCardAction, RemoveCardAction, ExhaustCardAction |
| User choices | `display.py` | SelectAction, DisplayTextAction |
| Rewards | `reward.py` | AddRelicAction, AddGoldAction, AddRandomPotionAction |
| Health | `health.py` | HealAction, LoseHPAction |
| Map navigation | `map_selection.py` | MoveToMapNodeAction, SelectMapNodeAction |
| Shop | `shop.py` | BuyItemAction |

## CONVENTIONS

**Required:**
- `@register("action")` decorator on all action classes
- `execute(self) -> BaseResult` method override
- Lazy import `game_state` inside execute method
- Return appropriate `ResultType` subclass
- Use `localize()` for all user-facing text

**Callable Parameters:**
- Damage/block/energy/count/heal amounts support callables (e.g., `lambda: game_state.player.block`)

**ActionQueue Usage:**
- Actions queued via `game_state.execute_all_actions()`
- Use `add_action(action, to_front=True)` for priority
- Use `add_actions([actions])` to batch enqueue

## ANTI-PATTERNS

**NEVER:**
- Create new GameFlow/GameState instances (use singleton via lazy import)
- Return strings like "WIN"/"DEATH" (use ResultType)
- Skip `@register("action")` decorator
- Call `game_state` at module level (import inside execute)
- Mix synchronous and asynchronous action handling

**ALWAYS:**
- Import `game_state` inside execute methods (not at module level)
- Return BaseResult subclass from actions
- Use `localize()` for all user-facing text
