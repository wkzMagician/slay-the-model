"""
Debug map generation to see consecutive room types.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def debug_seed(seed: int):
    """Debug map generation with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    print(f"\nSeed {seed}:")
    for f in range(len(nodes)):
        room_types = [n.room_type.name for n in nodes[f]]
        print(f"  Floor {f}: {room_types}")
    
    # Check for consecutive elite/rest/shop
    for f in range(1, len(nodes)):
        prev_types = {n.room_type for n in nodes[f-1]}
        curr_types = {n.room_type for n in nodes[f]}
        
        # Check if any elite/rest/shop appears in both floors
        problematic_types = {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}
        
        if prev_types & problematic_types:
            print(f"  Floor {f-1} has problematic: {[t.name for t in prev_types if t in problematic_types]}")
        
        if curr_types & problematic_types:
            print(f"  Floor {f} has problematic: {[t.name for t in curr_types if t in problematic_types]}")
        
        if prev_types & problematic_types and curr_types & problematic_types:
            overlap = prev_types & curr_types & problematic_types
            if overlap:
                print(f"  WARNING: Consecutive {overlap} on floors {f-1} and {f}")

if __name__ == "__main__":
    debug_seed(1)
    debug_seed(42)