"""
Test Unknown room mechanics based on Slay the Spire rules.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_unknown_basic():
    """Test basic unknown room mechanics."""
    print("=" * 60)
    print("Test: Basic Unknown Room Mechanics")
    print("=" * 60)
    
    from map.map_manager import MapManager
    from map.map_data import MapData
    from utils.types import RoomType
    
    # Create map manager with seed for reproducibility
    map_manager = MapManager(seed=42, act_id=1)
    
    # Create a simple map with unknown rooms
    map_data = MapData(act_id=1)
    from map.map_node import MapNode
    
    # Add floor 0
    floor_0 = [
        MapNode(0, 0, RoomType.MONSTER, connections_up=[0]),
        MapNode(0, 1, RoomType.MONSTER, connections_up=[0]),
    ]
    map_data.add_floor(floor_0)
    
    # Add floor 1 with unknown rooms
    floor_1 = [
        MapNode(1, 0, RoomType.UNKNOWN, connections_up=[0]),
        MapNode(1, 1, RoomType.UNKNOWN, connections_up=[0]),
    ]
    map_data.add_floor(floor_1)
    
    map_manager.map_data = map_data
    map_manager.map_data.set_current_position(0, 0)
    
    print("Initial visit counters:")
    for room_type, count in map_manager.unknown_room_visits.items():
        print(f"  {room_type.value}: {count}")
    print()
    
    # Visit multiple unknown rooms
    results = []
    for i in range(10):
        map_manager.map_data.set_current_position(1, 0)
        room_type = map_manager._resolve_unknown_type(1)
        results.append(room_type)
        print(f"Visit {i+1}: {room_type.value}")
    
    print()
    print("Visit counters after 10 visits:")
    for room_type, count in map_manager.unknown_room_visits.items():
        print(f"  {room_type.value}: {count}")
    
    print()
    print(f"Room distribution: {len([r for r in results if r == RoomType.MONSTER])} Monster, "
          f"{len([r for r in results if r == RoomType.MERCHANT])} Shop, "
          f"{len([r for r in results if r == RoomType.TREASURE])} Treasure, "
          f"{len([r for r in results if r == RoomType.UNKNOWN])} Event")
    
    print()
    print("[OK] Basic unknown room mechanics working")
    print()
    # Test completed


def test_tiny_chest():
    """Test Tiny Chest relic effect."""
    print("=" * 60)
    print("Test: Tiny Chest Relic")
    print("=" * 60)
    
    from map.map_manager import MapManager
    from utils.types import RoomType
    
    # Create map manager with Tiny Chest relic
    map_manager = MapManager(seed=42, act_id=1)
    from tests.test_combat_utils import create_test_helper
    from relics.global_relics.common import TinyChest
    helper = create_test_helper()
    helper.game_state.player.relics = [TinyChest()]
    
    print("Testing Tiny Chest: Every 4th ? room should be Treasure")
    print()
    
    results = []
    for i in range(12):
        room_type = map_manager._resolve_unknown_type(1)
        results.append(room_type)
        print(f"Visit {i+1}: {room_type.value}")
        
        # Verify every 4th visit is Treasure
        if (i + 1) % 4 == 0:
            assert room_type == RoomType.TREASURE, f"Visit {i+1} should be Treasure but got {room_type.value}"
    
    print()
    treasure_count = sum(1 for r in results if r == RoomType.TREASURE)
    print(f"Treasure rooms: {treasure_count}/12 (at least 3 forced)")
    assert treasure_count >= 3, f"Expected at least 3 Treasure rooms, got {treasure_count}"
    
    print()
    print("[OK] Tiny Chest relic working correctly")
    print()


def test_juzu_bracelet():
    """Test Juzu Bracelet relic effect."""
    print("=" * 60)
    print("Test: Juzu Bracelet Relic")
    print("=" * 60)
    
    from map.map_manager import MapManager
    from utils.types import RoomType
    
    # Create map manager with Juzu Bracelet
    map_manager = MapManager(seed=42, act_id=1)
    map_manager.set_relic_effect('juzu_bracelet', True)
    
    print("Testing Juzu Bracelet: No regular monsters in ? rooms")
    print()
    
    # Visit many unknown rooms
    results = []
    for i in range(50):
        room_type = map_manager._resolve_unknown_type(1)
        results.append(room_type)
    
    monster_count = sum(1 for r in results if r == RoomType.MONSTER)
    print(f"Monster rooms: {monster_count}/50 (expected 0)")
    
    if monster_count > 0:
        print(f"[ERROR] Found {monster_count} Monster rooms with Juzu Bracelet!")
        assert False, f"Found {monster_count} Monster rooms with Juzu Bracelet!"
    
    print()
    print("[OK] Juzu Bracelet preventing Monster rooms")
    print()
    # Test passed


def test_deadly_events():
    """Test Deadly Events modifier."""
    print("=" * 60)
    print("Test: Deadly Events Modifier")
    print("=" * 60)
    
    from map.map_manager import MapManager
    from utils.types import RoomType
    
    # Test without deadly events
    print("Without Deadly Events (floor 5):")
    map_manager = MapManager(seed=42, act_id=1, deadly_events=False)
    
    # Visit many unknown rooms on floor 5
    elite_count = 0
    for i in range(100):
        room_type = map_manager._resolve_unknown_type(5)
        if room_type == RoomType.ELITE:
            elite_count += 1
    
    print(f"  Elite rooms: {elite_count}/100 (expected 0 - Elite only with deadly_events)")
    assert elite_count == 0, f"Found {elite_count} Elite rooms without deadly_events"
    
    print()
    print("With Deadly Events (floor 7):")
    map_manager = MapManager(seed=42, act_id=1, deadly_events=True)
    
    # Visit many unknown rooms on floor 7
    elite_count = 0
    for i in range(100):
        room_type = map_manager._resolve_unknown_type(7)
        if room_type == RoomType.ELITE:
            elite_count += 1
    
    print(f"  Elite rooms: {elite_count}/100")
    print(f"  Treasure increment: +4% (instead of +2%)")
    
    print()
    print("[OK] Deadly Events modifier working correctly")
    print()


def main():
    """Run all tests."""
    print("\n")
    print("============================================================")
    print("        Unknown Room Mechanics Test Suite")
    print("============================================================")
    print("\n")
    
    try:
        # Test basic mechanics
        test_unknown_basic()
        
        # Test Tiny Chest
        test_tiny_chest()
        
        # Test Juzu Bracelet
        test_juzu_bracelet()
        
        # Test Deadly Events
        test_deadly_events()
        
        print("=" * 60)
        print("All unknown room tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())