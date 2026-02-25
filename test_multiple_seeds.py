"""
Test map generation with multiple seeds to verify constraint enforcement.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_seed(seed: int) -> bool:
    """Test map generation with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    # Check for consecutive elite/rest/shop (same type)
    for f in range(1, len(nodes)):
        prev_types = {n.room_type for n in nodes[f-1]}
        curr_types = {n.room_type for n in nodes[f]}
        
        # Check if same elite/rest/shop type appears in both consecutive floors
        # This means: Floor 4 has MERCHANT and Floor 5 also has MERCHANT (bad)
        # But: Floor 4 has MERCHANT and Floor 5 has REST/ELITE (OK)
        for problem_type in {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}:
            if problem_type in prev_types and problem_type in curr_types:
                print(f"  FAILED: Seed {seed} - Consecutive {problem_type.name} on floors {f-1} and {f}")
                return False
    
    return True

if __name__ == "__main__":
    seeds = [1, 42, 100, 999, 12345, 666, 777, 8888]
    
    print("=" * 60)
    print("Testing Multiple Seeds")
    print("=" * 60)
    
    all_passed = True
    for seed in seeds:
        passed = test_seed(seed)
        if not passed:
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All seeds passed!")
    else:
        print("FAILURE: Some seeds failed!")
    print("=" * 60)