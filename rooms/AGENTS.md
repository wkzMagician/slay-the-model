# SLAY THE MODEL - ROOMS

**Generated:** 2026-02-20
**Commit:** ef19e04
**Branch:** main

## OVERVIEW

Map exploration room types with enter() logic for game progression.

## KEY CLASSES

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `Room` | class | `base.py` | Base room class, enter() hook |
| `CombatRoom` | class | `combat.py` | Enemy encounters, starts combat |
| `RestRoom` | class | `rest.py` | REST (heal) or UPGRADE choices |
| `ShopRoom` | class | `shop.py` | Buy cards, relics, potions |
| `TreasureRoom` | class | `treasure.py` | Gold/relic rewards |
| `EventRoom` | class | `event.py` | Random events with choices |
| `NeoRoom` | class | `neo.py` | Starter card selection |

## ROOM TYPES

- CombatRoom: Creates enemies, starts combat via engine
- RestRoom: 25% HP heal or card upgrade
- ShopRoom: 3 cards, 1 relic, 1 potion for sale
- TreasureRoom: Choose gold or relic reward
- EventRoom: Random event from events/ module
- NeoRoom: Starter card selection (Act 1 only)

## ANTI-PATTERNS

- NO bypassing room transitions via direct state changes
- NO starting combat outside CombatRoom.enter()
- NO modifying player gold/relics without room context
- NO accessing GameFlow directly from rooms

## ADDING NEW ROOMS

1. Inherit from Room in `base.py`
2. Implement enter() method
3. Add to room type enum
4. Handle room completion/cleanup
