Bugs:

# 1

============================================================
MAP VIEW
============================================================

Legend:
  [M]=Monster  [E]=Elite  [$]=Merchant  [?]=Event
  [R]=Rest     [T]=Treasure  [B]=Boss  [N]=Neo
  *=Current   >=Available   ^=Visited
  Connections: /=left  |=center  \=right

Floor  0: [ N ]
           /|\
Floor  1: [^M ][ M ][ M ]
            |   /    /|
Floor  2: [^R ][ M ][ ? ][ M ]
            |\  /    /     |
Floor  3: [^M ][ ? ][ M ]
            |\  /    /|
Floor  4: [^M ][ R ][ M ][ ? ]
            |\  /    / \   |
Floor  5: [^? ][ ? ][ ? ]
            |   /|   /|
Floor  6: [^M ][ ? ][ M ][ M ][ ? ]
            |   / \  /     |\  /|
Floor  7: [^? ][ M ][ M ][ M ]
            |    |   /    /|
Floor  8: [^M ][ M ][ M ][ E ][ M ]
            |\  /     |   /     |
Floor  9: [^T ][ T ][ T ]
            |   / \  /|
Floor 10: [^? ][ M ][ M ][ M ]
            |\  /|   /    /|
Floor 11: [^? ][ R ][ M ][ M ][ $ ]
            |   /     |   /    /|
Floor 12: [^R ][ M ][ ? ]
            |   /|   /|
Floor 13: [^M ][ R ][ M ][ M ][ M ]
            |\  /    /    /|    |
Floor 14: [^R ][ ? ][ R ][ ? ]
            |   /    /     |
Floor 15: [*R ][ R ][ R ]
             \   |   /
Floor 16: [>B ]
            |
Floor 17: [ T ]

============================================================

[AI Debug] Map Context:
  Current Floor: 15
  Current Position: 0
  Available Moves: 1

[AI Debug] ASCII Map:
Floor  0: [X]
        |/
Floor  1: [X] [X] [X]
        |   |   |/
Floor  2: [X] [X] [X] [X]
        |/  \   \   \
Floor  3: [X] [X] [X]
        |/  |   |/
Floor  4: [X] [X] [X] [X]
        |/  \   \|  \
Floor  5: [X] [X] [X]
        |   |/  /
Floor  6: [X] [X] [X] [X] [X]
        |   \/  \   \|  \
Floor  7: [X] [X] [X] [X]
        |   |   |   |/
Floor  8: [X] [X] [X] [X] [X]
        |/  \   \   \   \
Floor  9: [X] [X] [X]
        |   |/  |/
Floor 10: [X] [X] [X] [X]
        |/  \|  |   |/
Floor 11: [X] [X] [X] [X] [X]
        |   \   \   \   \
Floor 12: [X] [X] [X]
        |   |/  |/
Floor 13: [X] [X] [X] [X] [X]
        |/  \   \   \   \
Floor 14: [X] [X] [X] [X]
        |   \   \   \
Floor 15: [*R] [R] [R]
        |   \   \
Floor 16: [>B]
        |
Floor 17: [T]

[AI Debug] Available Moves:
  [0] Floor 16, Pos 0: Boss (Risk: VERY_HIGH, Reward: VERY_HIGH)
[AI Debug] Strategy: first
[AI Debug] Choosing move at index 0:
  Floor: 16
  Position: 0
  Room Type: Boss
  Risk Level: VERY_HIGH
  Reward Level: VERY_HIGH
You discovered a treasure room!
（这里游戏就结束了）

为什么没有打boss？
为什么没有进入act2？

# 2

这打了牌手牌怎么没有减少啊？

Hand (5):
  [1] Bash (Cost: 2, Type: Attack, Rarity: Starter)
Deal 8 damage. Apply 2 Vulnerable.
  [2] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [3] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [4] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [5] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.

Powers:
  Buffer x999
    Prevents the next 999 times you would lose HP.

=== Enemies ===

Red Louse:
  HP: 14/14
  Block: 0
  Powers:
    Curl Up x5
      On damage, gains 5 Block.
  Intention: Deal 7 damage.

Green Louse:
  HP: 16/16
  Block: 0
  Powers:
    Curl Up x7
      On damage, gains 7 Block.
  Intention: Apply 1 Weak to you.

--- Combat Status ---

=== Choose an action ===
1. Bash (Cost: 2, Type: Attack, Rarity: Starter)
Deal 8 damage. Apply 2 Vulnerable.
2. Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
3. Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
4. Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
5. Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
6. End turn

Selected:
  1. Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
Played Defend
Ironclad gains 5 block

--- Combat Status ---
HP: 88/88
Block: 10
Energy: 1/3

Hand (5):
  [1] Bash (Cost: 2, Type: Attack, Rarity: Starter)
Deal 8 damage. Apply 2 Vulnerable.
  [2] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [3] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [4] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
  [5] Defend (Cost: 1, Type: Skill, Rarity: Starter)
Gain 5 Block.
---

## Fixes Applied (2024-02-19)

### Bug #1: Boss room shows treasure instead of boss fight
**Status: FIXED**
**File**: `map/map_manager.py`
**Issue**: `RoomType.BOSS` was returning `TreasureRoom` instead of `CombatRoom`
**Fix**: Changed `_create_room_instance()` to return `CombatRoom` for BOSS type

### Bug #2: Hand count doesn't decrease after playing card
**Status: NEEDS INVESTIGATION**
**Issue**: Cards stay in hand after being played - should move to discard pile
**Related**: `PlayCardBHAction`, `DiscardCardAction`, `execute_all_actions()`

---

## Test Results Summary

### Progress
- **Before**: 569 passed, 97 failed
- **After**: 621 passed, 47 failed

### Game Bugs Fixed (7)
1. Boss room returns CombatRoom instead of TreasureRoom
2. SlimeBoss intention naming (`slime_boss_slam` → `slam`)
3. Added `RoomType.NORMAL` enum
4. `Power.info()` now includes Duration and Amount
5. `Potion.info()` now includes Rarity and Category
6. Implemented `ChampionBelt.on_apply_power()`
7. `DarkOrb.on_evoke()` handles no-target case gracefully

### Remaining Failures (47)
- **test_enemy_intentions.py** (9): Cultist/Louse intention pattern bugs
- **test_event_pool.py** (1): Decorator registration issue
- **test_gold_simple.py** (3): Test design bug (MockCombatRoom)
- **test_orb_actions.py** (5): Test design bug (no combat setup)
- **test_rooms.py** (1): Test expects wrong behavior (TreasureRoom for BOSS)

### Cannot Fix Without Modifying Tests (9 tests)
These tests have design issues where they expect behavior that contradicts game logic:
- `test_gold_simple.py`: MockCombatRoom lacks required methods
- `test_orb_actions.py`: Tests don't set up combat state with enemies
- `test_rooms.py`: Test expects BOSS → TreasureRoom (wrong game behavior)
