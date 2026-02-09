# ROOMS DIRECTORY KNOWLEDGE BASE

## OVERVIEW
8 room types managing game flow (combat, rest, shop, treasure, events).

## ROOM TYPES

| Room Type | File | Purpose |
|-----------|------|---------|
| `Room` | base.py | Base class with init(), enter(), leave() lifecycle |
| `EventRoom` | event.py | Random events based on floor |
| `CombatRoom` | combat.py | Normal/Elite/Boss fights with rewards |
| `RestRoom` | rest.py | Heal, upgrade cards, remove cards |
| `ShopRoom` | shop.py | Buy cards, potions, relics, remove cards |
| `TreasureRoom` | treasure.py | Chest rooms (Small/Medium/Large/Boss) |
| `NeoRewardRoom` | neo.py | Starting room with Neo blessing |

## WHERE TO LOOK
| Task | File | Pattern |
|------|----------|---------|
| Add room type | Create file, inherit `Room` | Use `@register("room")` decorator |
| Combat rewards | combat.py | Gold + card/potion by difficulty |
| Rest options | rest.py | Heal/upgrade/remove with relic modifiers |
| Shop items | shop.py | 5 colored + 2 colorless cards, 3 potions, 3 relics |

## CONVENTIONS

**Lifecycle (CRITICAL):**
1. `__init__(**kwargs)` - Initialize, set `room_type`
2. `init()` - Setup room-specific data (BEFORE enter)
3. `enter() -> BaseResult` - Main logic loop
4. `leave()` - Cleanup on exit

**Action Queue:**
- Always use `game_state.action_queue.add_action()`
- Clear queue: `game_state.action_queue.clear()` before each iteration
- Menu pattern: `while not should_leave` → build options → execute → repeat

**Reward Systems:**
- Boss: 150 gold, 1 potion
- Elite: 50 gold, 1 card, 1 potion
- Normal: enemy gold_reward, 1 card
- Shop: 5 colored (1 50% discount), 2 colorless, 3 potions, 3 relics

## ANTI-PATTERNS

**NEVER:**
- Return string results ("WIN"/"DEATH") from `enter()` → use `GameStateResult(ResultType.VICTORY/DEATH)`
- Skip `init()` when room needs setup
- Block inside `enter()` without clearing action queue
- Create rooms without `@register("room")` decorator

**ALWAYS:**
- Inherit from `Room` base class
- Import `game_state` inside methods (avoid circular imports)
- Return `BaseResult` from `enter()`
- Set `should_leave = True` before exiting
- Use `LeaveRoomAction(room=self)` for transitions

## SPECIAL CASES

**EventRoom:** Triggers random event based on floor (early/mid/late/boss)
**NeoRewardRoom:** Delegates to `events.neo_event.NeoEvent.trigger()` (starting room)
**Shop Relic Modifiers:** MembershipCard (50% off), TheCourier (restock + 20% off), SmilingMask (removal fixed at 50g)
