"""
Debug script to check _assign_fixed_floors execution.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_fixed_floors_assignment(seed: int):
    """Test fixed floors assignment."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    print(f"\n=== Testing Seed {seed} ===")
    
    # Total number of floors
    print(f"\nTotal floors in map: {len(nodes)}")
    
    # Check floor 9 (index 8)
    if 8 < len(nodes):
        print(f"\nFloor 9 (index 8) has {len(nodes[8])} nodes:")
        for pos, node in enumerate(nodes[8]):
            print(f"  Position {pos}: room_type = {node.room_type.name}")
    else:
        print(f"\nERROR: Floor index 8 out of range (total floors: {len(nodes)})")
    
    # Check if any node on floor 9 is TREASURE
    has_treasure = any(node.room_type == RoomType.TREASURE for node in nodes[8])
    print(f"\nFloor 9 has TREASURE: {has_treasure}")
    
    # Check floor 15 (index 14)
    print(f"\nFloor 15 (index 14) has {len(nodes[14])} nodes:")
    for pos, node in enumerate(nodes[14]):
        print(f"  Position {pos}: room_type = {node.room_type.name}")
    
    # Check if any node on floor 15 is REST
    has_rest = any(node.room_type == RoomType.REST for node in nodes[14])
    print(f"\nFloor 15 has REST: {has_rest}")
    
    # Print all floors with their room types
    print(f"\n=== All Floors ===")
    for floor in range(len(nodes)):
        floor_types = [node.room_type.name for node in nodes[floor]]
        print(f"Floor {floor}: {floor_types}")

if __name__ == "__main__":
    test_fixed_floors_assignment(1)
