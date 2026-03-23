"""
Comprehensive test for all map generation constraints.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_all_constraints(seed: int):
    """Test all map generation constraints with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    print(f"\nTesting Seed {seed}:")
    
    # Constraint 1: Floor 0 is NEO
    assert nodes[0][0].room_type == RoomType.NEO, "Floor 0 is not NEO"
    print(f"  [OK] Floor 0 is NEO")
    
    # Constraint 2: Floor 9 (index 9) is TREASURE
    floor_9_types = {n.room_type for n in nodes[9]}
    floor_9_room_types = [n.room_type.name for n in nodes[9]]
    print(f"  Floor 9 (index 9) room types: {floor_9_room_types}")
    assert RoomType.TREASURE in floor_9_types, "Floor 9 doesn't have TREASURE room"
    print(f"  [OK] Floor 9 has TREASURE")
    
    # Constraint 3: Floor 15 (index 15) is REST
    floor_15_types = {n.room_type for n in nodes[15]}
    assert RoomType.REST in floor_15_types, "Floor 15 doesn't have REST room"
    print(f"  [OK] Floor 15 has REST")
    
    # Constraint 4: Floors 2-4 don't have ELITE or REST
    for f in range(2, 5):
        floor_types = {n.room_type for n in nodes[f]}
        assert RoomType.ELITE not in floor_types, f"Floor {f} has ELITE (not allowed in first 5)"
        assert RoomType.REST not in floor_types, f"Floor {f} has REST (not allowed in first 5)"
    print(f"  [OK] Floors 2-4 don't have ELITE or REST")
    
    # Constraint 5: Floor 14 doesn't have REST
    floor_14_types = {n.room_type for n in nodes[14]}
    assert RoomType.REST not in floor_14_types, "Floor 14 has REST (not allowed)"
    print(f"  [OK] Floor 14 doesn't have REST")
    
    # Constraint 6: No consecutive ELITE/REST/MERCHANT
    for f in range(1, len(nodes)):
        prev_types = {n.room_type for n in nodes[f-1]}
        curr_types = {n.room_type for n in nodes[f]}
        
        for problem_type in {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}:
            assert not (
                problem_type in prev_types and problem_type in curr_types
            ), f"Consecutive {problem_type.name} on floors {f-1} and {f}"
    print(f"  [OK] No consecutive ELITE/REST/MERCHANT")

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
