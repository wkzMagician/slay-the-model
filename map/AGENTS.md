# MAP SYSTEM KNOWLEDGE BASE

## OVERVIEW
Map generation and room placement across 16 floors with branching paths.

## STRUCTURE
```
map/
├── base.py             # Base map classes
├── map_data.py         # Map data structures
├── map_node.py         # Room node representation
├── map_manager.py      # Core map logic (715 lines)
└── encounter_pool.py    # Enemy/spawn pools
```

## WHERE TO LOOK
| Task | File | Notes |
|------|-------|-------|
| Map generation | `map_manager.py:generate_map()` | Creates branching paths per floor |
| Room connections | `map_node.py` | Parent/child relationships |
| Enemy pools | `encounter_pool.py` | Floor-appropriate enemy selection |
| Map data storage | `map_data.py` | Per-floor map state |

## CONVENTIONS

**MapNode Structure:**
- Each node: one room type (combat, event, rest, shop, treasure)
- Parent/child relationships for path tracking
- Visited status for navigation

**Map Generation:**
- Branching paths (not linear dungeon)
- 3-5 nodes per floor
- Elite and boss nodes fixed on paths
- Treasure and rest nodes randomly placed

**Encounter Pools:**
- Early floors (1-4): weak enemies
- Mid floors (5-10): mixed difficulty
- Late floors (11-15): stronger enemies
- Boss floors (3, 8, 11, 15): boss nodes

## ANTI-PATTERNS

**NEVER:**
- Create maps with linear paths (must branch)
- Skip elite node generation (required at floors 3, 8, 11, 15)
- Place boss nodes on wrong floors

**ALWAYS:**
- Use `MapNode` for all room representations
- Call `map_manager.generate_map(floor)` before room navigation
- Check `node.visited` before entering rooms
