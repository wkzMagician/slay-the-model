"""
Test script for map generation logic.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_map_generation():
    """Test that map generation follows all constraints."""
    print("=" * 60)
    print("Testing Map Generation")
    print("=" * 60)
    
    # Create map manager and generate map
    mm = MapManager(seed=42, act_id=1)
    mm.generate_map()
    
    total_floors = len(mm.map_data.nodes)
    print(f"\nTotal floors: {total_floors}")
    
    # Display room types per floor
    print(f"\nRoom types per floor:")
    for f in range(total_floors):
        room_types = [node.room_type.name for node in mm.map_data.nodes[f]]
        print(f"  Floor {f}: {room_types}")
    
    # Verify constraints
    print("\nConstraints check:")
    
    # Fixed floors
    floor0_neo = all(n.room_type == RoomType.NEO for n in mm.map_data.nodes[0])
    print(f"Floor 0 (NEO): {floor0_neo}")
    
    floor1_monster = all(n.room_type == RoomType.MONSTER for n in mm.map_data.nodes[1])
    print(f"Floor 1 (Monster): {floor1_monster}")
    
    floor9_treasure = all(n.room_type == RoomType.TREASURE for n in mm.map_data.nodes[9])
    print(f"Floor 9 (Treasure): {floor9_treasure}")
    
    floor15_rest = all(n.room_type == RoomType.REST for n in mm.map_data.nodes[15])
    print(f"Floor 15 (Rest): {floor15_rest}")
    
    floor16_boss = all(n.room_type == RoomType.BOSS for n in mm.map_data.nodes[16])
    print(f"Floor 16 (Boss): {floor16_boss}")
    
    floor17_treasure = all(n.room_type == RoomType.TREASURE for n in mm.map_data.nodes[17])
    print(f"Floor 17 (Treasure): {floor17_treasure}")
    
    # No elite/rest in floors 2-4
    no_elite_rest_early = all(
        all(n.room_type not in [RoomType.ELITE, RoomType.REST] for n in mm.map_data.nodes[f])
        for f in range(2, 6)
    )
    print(f"\nNo elite/rest in floors 2-4: {no_elite_rest_early}")
    
    # No rest on floor 14
    no_rest_14 = all(n.room_type != RoomType.REST for n in mm.map_data.nodes[14])
    print(f"No rest on floor 14: {no_rest_14}")
    
    # Only connected parent/child rooms constrain one another. Unrelated
    # routes may contain the same room type on neighboring rows (RUN-024).
    has_consecutive = False
    for floor, row in enumerate(mm.map_data.nodes[:-1]):
        for node in row:
            if node.room_type not in (RoomType.ELITE, RoomType.REST, RoomType.MERCHANT):
                continue
            for destination in node.connections_up:
                if mm.map_data.nodes[floor + 1][destination].room_type == node.room_type:
                    has_consecutive = True

    if not has_consecutive:
        print("\nNo consecutive elite/rest/shop: True")
    else:
        print("\nNo consecutive elite/rest/shop: False")
    
    # Final result
    all_checks = (
        floor0_neo and
        floor1_monster and
        floor9_treasure and
        floor15_rest and
        floor16_boss and
        floor17_treasure and
        no_elite_rest_early and
        no_rest_14 and
        not has_consecutive
    )
    
    print("\n" + "=" * 60)
    if all_checks:
        print("SUCCESS: All constraints passed!")
    else:
        print("FAILURE: Some constraints failed!")
    print("=" * 60)

    assert all_checks

if __name__ == "__main__":
    test_map_generation()
