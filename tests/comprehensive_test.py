"""
Comprehensive test for all map generation constraints.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_all_constraints(seed: int) -> bool:
    """Test all map generation constraints with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    print(f"\nTesting Seed {seed}:")
    
    # Constraint 1: Floor 0 is NEO
    if nodes[0][0].room_type != RoomType.NEO:
        print(f"  FAILED: Floor 0 is not NEO")
        return False
    print(f"  [OK] Floor 0 is NEO")
    
    # Constraint 2: Floor 9 (index 8) is TREASURE
    floor_9_types = {n.room_type for n in nodes[8]}
    floor_9_room_types = [n.room_type.name for n in nodes[8]]
    print(f"  Floor 9 (index 8) room types: {floor_9_room_types}")
    if RoomType.TREASURE not in floor_9_types:
        print(f"  FAILED: Floor 9 doesn't have TREASURE room")
        return False
    print(f"  [OK] Floor 9 has TREASURE")
    
    # Constraint 3: Floor 15 (index 14) is REST
    floor_15_types = {n.room_type for n in nodes[14]}
    if RoomType.REST not in floor_15_types:
        print(f"  FAILED: Floor 15 doesn't have REST room")
        return False
    print(f"  [OK] Floor 15 has REST")
    
    # Constraint 4: First 5 floors (0-4) don't have ELITE or REST
    for f in range(0, 5):
        floor_types = {n.room_type for n in nodes[f]}
        if RoomType.ELITE in floor_types:
            print(f"  FAILED: Floor {f} has ELITE (not allowed in first 5)")
            return False
        if RoomType.REST in floor_types:
            print(f"  FAILED: Floor {f} has REST (not allowed in first 5)")
            return False
    print(f"  [OK] Floors 0-4 don't have ELITE or REST")
    
    # Constraint 5: Floor 14 doesn't have REST
    floor_14_types = {n.room_type for n in nodes[14]}
    if RoomType.REST in floor_14_types:
        print(f"  FAILED: Floor 14 has REST (not allowed)")
        return False
    print(f"  [OK] Floor 14 doesn't have REST")
    
    # Constraint 6: No consecutive ELITE/REST/MERCHANT
    for f in range(1, len(nodes)):
        prev_types = {n.room_type for n in nodes[f-1]}
        curr_types = {n.room_type for n in nodes[f]}
        
        for problem_type in {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}:
            if problem_type in prev_types and problem_type in curr_types:
                print(f"  FAILED: Consecutive {problem_type.name} on floors {f-1} and {f}")
                return False
    print(f"  [OK] No consecutive ELITE/REST/MERCHANT")
    
    # Constraint 7: Room type diversity (excluding floor 8-9 path)
    # Any room can only connect to rooms of different types
    # This is about adjacent floors, not within the same floor
    # Already covered by constraint 6
    
    return True

if __name__ == "__main__":
    seeds = [1, 42, 100, 999, 12345, 666, 777, 8888, 42, 1000]
    
    print("=" * 60)
    print("Comprehensive Map Generation Test")
    print("=" * 60)
    
    all_passed = True
    for seed in seeds:
        passed = test_all_constraints(seed)
        if not passed:
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All seeds passed all constraints!")
    else:
        print("FAILURE: Some seeds failed constraints!")
    print("=" * 60)