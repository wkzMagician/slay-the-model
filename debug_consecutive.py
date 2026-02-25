"""
Debug consecutive room type check logic.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def debug_consecutive():
    """Debug the consecutive room type checking logic."""
    mm = MapManager(seed=1, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    print("\nDetailed Consecutive Check:")
    
    for f in range(1, len(nodes)):
        print(f"\n--- Checking Floor {f-1} to Floor {f} ---")
        
        # Get room types on both floors
        prev_floor_types = {n.room_type for n in nodes[f-1]}
        curr_floor_types = {n.room_type for n in nodes[f]}
        
        print(f"Floor {f-1} types: {[t.name for t in prev_floor_types]}")
        print(f"Floor {f} types: {[t.name for t in curr_floor_types]}")
        
        # Problematic types to check
        problematic_types = {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}
        
        prev_problematic = prev_floor_types & problematic_types
        curr_problematic = curr_floor_types & problematic_types
        
        print(f"Floor {f-1} has problematic types: {prev_problematic}")
        print(f"Floor {f} has problematic types: {curr_problematic}")
        
        # Check if both have problematic types
        if prev_problematic and curr_problematic:
            overlap = prev_problematic & curr_problematic
            print(f"  Both floors have problematic types")
            print(f"  Overlap: {overlap}")
            
            # My code filters available types based on this
            filtered = {RoomType.MONSTER, RoomType.ELITE, RoomType.REST, 
                       RoomType.MERCHANT, RoomType.EVENT}
            
            # If previous floor has REST/ELITE/MERCHANT, avoid those types
            if prev_problematic:
                filtered = {t for t in filtered if t not in prev_problematic}
            
            print(f"  Available after filtering: {filtered}")
            
            if not filtered:
                print(f"  ERROR: No available types!")
        else:
            print(f"  OK: One or both floors don't have problematic types")

if __name__ == "__main__":
    debug_consecutive()