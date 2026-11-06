"""
Test map generation with multiple seeds to verify constraint enforcement.
"""
from map.map_manager import MapManager
from utils.types import RoomType

def test_seed(seed: int) -> None:
    """Test map generation with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes
    
    # Original restrictions apply to actual edges, not the entire adjacent row.
    for floor, row in enumerate(nodes[:-1]):
        for node in row:
            if node.room_type in (RoomType.ELITE, RoomType.REST, RoomType.MERCHANT):
                for destination in node.connections_up:
                    assert nodes[floor + 1][destination].room_type != node.room_type, (
                        f"Connected consecutive {node.room_type.name} at {floor}:{node.position}"
                    )

if __name__ == "__main__":
    seeds = [1, 42, 100, 999, 12345, 666, 777, 8888]
    
    print("=" * 60)
    print("Testing Multiple Seeds")
    print("=" * 60)
    
    for seed in seeds:
        test_seed(seed)
    
    print()
    print("=" * 60)
    print("SUCCESS: All seeds passed!")
    print("=" * 60)
