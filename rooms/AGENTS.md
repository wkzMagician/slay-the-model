# ROOMS DIRECTORY - DOMAINS

**Generated:** 2026-02-07
**Files:** 7 (base.py, combat.py, rest.py, shop.py, treasure.py, neo.py, __init__.py)

## ROOM TYPES

| Room Type | File | Purpose | Key Features |
|-----------|------|---------|--------------|
| `Room` | base.py | Base class for all rooms | init(), enter(), leave() lifecycle |
| `UnknownRoom` | base.py | Placeholder that resolves on enter | Becomes event or actual room |
| `CombatRoom` | combat.py | Manage combat execution | Normal/Elite/Boss variants, rewards |
| `RestRoom` | rest.py | Rest site with services | Heal, upgrade cards, remove cards, relic interactions |
| `ShopRoom` | shop.py | Merchant room | 5 colored, 2 colorless cards, 3 potions, 3 relics, card removal |
| `TreasureRoom` | treasure.py | Chest rooms | Small/Medium/Large/Boss chests |
| `NeoRewardRoom` | neo.py | Starting room | Triggers Neo blessing event |

## WHERE TO LOOK

| Task | Location | Pattern |
|------|----------|---------|
| Add new room type | Create file in rooms/ | Inherit from `Room`, use `@register("room")` decorator |
| Room lifecycle hooks | base.py `Room` class | `__init__()`, `init()`, `enter()`, `leave()` |
| Combat rewards | combat.py `_handle_victory()` | Gold, card (non-boss), potion (elite/boss) |
| Rest options | rest.py `_build_rest_menu()` | Heal, upgrade, remove, relic-specific options |
| Shop pricing | shop.py `_generate_items()` | Rarity-based pricing, 50% discount on random card |
| Relic price modifiers | shop.py `ShopItem.get_final_price_with_modifiers()` | MembershipCard, TheCourier, SmilingMask |
| Chest opening logic | treasure.py `_build_treasure_menu()` | OpenChestAction, chest type randomization |

## CONVENTIONS

### Room Architecture

**Lifecycle (CRITICAL - must follow order):**
1. `__init__(**kwargs)` - Initialize with kwargs, set `room_type`
2. `init()` - Called BEFORE enter(), setup room-specific data
3. `enter() -> BaseResult` - Main room logic loop
4. `leave()` - Cleanup when player exits

**Action Queue Integration:**
- Always use `game_state.action_queue.add_action()`
- Main loop pattern: `while not self.should_leave` → build menu → execute → repeat
- Clear queue before each iteration: `game_state.action_queue.clear()`

**Menu Building:**
- Create `_build_X_menu()` methods that return `Option[]`
- Options use `Option(name, actions=[])` structure
- Present via `SelectAction(title, options)`

### Reward Systems

**Combat Rewards:**
- Boss: 150 gold, 1 potion
- Elite: 50 gold, 1 random card, 1 potion
- Normal: Sum of enemy `gold_reward` attributes, 1 random card

**Shop Generation:**
- 5 colored cards (2 attacks, 2 skills, 1 power) - one 50% discount
- 2 colorless cards (1 uncommon, 1 rare) - 20% more expensive
- 3 potions (weight: 65% common, 25% uncommon, 10% rare)
- 3 relics (rightmost is Shop relic, weight: 50% common, 33% uncommon, 17% rare)
- Card removal: 75 gold base, +25 per use, limited once per shop

**Rest Site Options:**
- Heal: 30% max_hp (+15 if RegalPillow), blocked by CoffeeDripper/MarkOfTheBloom
- Smith: Upgrade deck card, blocked by FusionHammer
- Remove: PeacePipe allows remove card option
- Dig: Shovel grants random relic
- Lift: Girya allows strength upgrade (TODO)

### Localization

- All rooms inherit `Localizable` from base
- Use `self.local("rooms.room_type.action", **vars)`
- Standard keys: `"rooms.combat.enter"`, `"rooms.rest.smith"`, etc.
- Default text provided in DisplayTextAction for missing keys

## ANTI-PATTERNS

**NEVER do these:**
- Return string results ("WIN"/"DEATH") from `enter()` → use `GameStateResult(ResultType.VICTORY/DEATH)`
- Skip `init()` method when room needs setup (enemy generation, item creation)
- Hardcode room creation logic → use `map_manager._create_room_instance()` and `_resolve_unknown_type()`
- Block inside `enter()` without clearing action queue
- Create rooms without `@register("room")` decorator (prevents registry lookup)

**ALWAYS do these:**
- Inherit from `Room` base class in rooms/base.py
- Import `game_state` inside methods (not top-level) to avoid circular imports
- Return `BaseResult` (NoneResult or GameStateResult) from `enter()`
- Set `self.should_leave = True` in leave() or when ready to exit
- Use `LeaveRoomAction(room=self)` for room transitions

## SPECIAL CASES

**UnknownRoom (base.py):**
- Resolves to `RoomType.EVENT` (via `event_pool.get_random_event()`) or actual room
- Marks unique events as used via `event_pool.mark_event_used()`
- Fallback to `RoomType.MONSTER` if map manager unavailable

**NeoRewardRoom (neo.py):**
- Special starting room (no standard RoomType)
- Delegates all logic to `events.neo_event.NeoEvent.trigger()`
- Auto-sets `should_leave = True` after event completes

**Shop Relic Interactions (shop.py):**
- `MembershipCard`: 50% discount on ALL items
- `TheCourier`: 20% discount on restocked items + restock on purchase
- `SmilingMask`: Card removal fixed at 50 gold (overrides price increases)
- Order: Base → Ascension modifier → MembershipCard → TheCourier → SmilingMask
