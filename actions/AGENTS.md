# ACTIONS DIRECTORY KNOWLEDGE BASE

**Generated:** 2026-02-07
**Files:** 13 action modules

## OVERVIEW
All game mechanics flow through action classes that inherit from `actions.base.Action`.
Actions return `ResultType` subclasses from `utils.result_types` to drive game flow.

## ACTION CLASS PATTERN

**Structure:**
```python
@register("action")
class MyAction(Action):
    def __init__(self, required_param, optional_param=None):
        self.required_param = required_param
        self.optional_param = optional_param

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state  # Lazy import pattern
        # Action logic here
        return NoneResult()  # Or other ResultType
```

**ResultType Returns:**
- `NoneResult()`: Action completed, no follow-up
- `SingleActionResult(action)`: Queue one action next (e.g., SelectAction)
- `MultipleActionsResult([actions])`: Queue multiple actions
- `GameStateResult`: Win/Death/end-game transition

## WHERE TO LOOK

| Task | File | Key Actions |
|------|-------|-------------|
| Damage/block/status | `combat.py` | DealDamageAction, GainBlockAction |
| Card play/energy | `combat.py` | PlayCardAction, GainEnergyAction, EndTurnAction |
| Card manipulation | `card.py` | AddCardAction, RemoveCardAction, TransformCardAction, ExhaustCardAction |
| User choices | `display.py` | SelectAction, DisplayTextAction |
| Rewards | `reward.py` | AddRelicAction, AddGoldAction, AddRandomPotionAction |
| Health | `health.py` | HealAction, LoseHPAction |
| Map navigation | `map_selection.py` | MoveToMapNodeAction, SelectMapNodeAction |
| Shop | `shop.py` | BuyItemAction |
| Events | `misc.py` | StartEventAction, EndEventAction |

## CONVENTIONS

**Required:**
- `@register("action")` decorator on all action classes
- `execute(self) -> 'BaseResult'` method override
- Lazy import `game_state` inside execute method
- Return appropriate `ResultType` subclass
- Use `t()` function for all user-facing text

**Callable Parameters:**
- Damage/block/energy/count/heal amounts support callables: `self._damage` property checks `callable(self._damage)`
- Allows dynamic values: `DealDamageAction(damage=lambda: game_state.player.block)`

**User Selection Pattern:**
- SelectAction accepts `List[Option]` where each `Option` has `name` and `actions`
- Single option auto-selects in AI mode or if `auto_select_single_option=True`
- Debug mode auto-selects first option

**ActionQueue Usage:**
- Actions are queued via `game_state.execute_all_actions()`
- Use `add_action(action, to_front=True)` for priority
- Use `add_actions([actions])` to batch enqueue

## ANTI-PATTERNS

**Never:**
- Create new GameFlow/GameState instances (use singleton via lazy import)
- Return strings like "WIN"/"DEATH" (use ResultType)
- Skip `@register("action")` decorator
- Call `game_state` at module level (import inside execute)
- Mix synchronous and asynchronous action handling

**Avoid:**
- Direct mutation of game_state without going through action pattern
- Circular imports with engine.game_state at file level
- Returning None instead of NoneResult()

## DOMAIN-SPECIFIC NOTES

**Combat Actions:**
- Strength modifies damage in DealDamageAction
- Weak reduces damage to 75% (artifact prevents)
- Frail reduces block to 75% (artifact prevents)
- Vulnerable tracked for next attack bonus

**Card Actions:**
- ExhaustCardAction triggers `on_exhaust` powers before card.on_exhaust()
- TransformCardAction removes card, adds random from same namespace
- Choose*CardAction actions create SelectAction with Option wrappers

**Display Actions:**
- SelectAction adds "return to menu" option for human players (via `add_menu_option_if_human`)
- Auto-selection logic: 1 option auto-selects, 0 options returns empty list
- Debug mode always selects first option
