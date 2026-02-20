"""
Test script for the map system.
"""
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map import MapManager, MapNode, MapData
from utils.types import RoomType

import pytest

@pytest.fixture
def manager():
    """Create a MapManager instance for testing."""
    m = MapManager(seed=12345, act_id=1)
    m.generate_map()
    return m


def test_map_generation():
    """Test basic map generation."""
    print("=" * 60)
    print("Test 1: Map Generation")
    print("=" * 60)
    
    # Create map manager with a fixed seed for reproducibility
    manager = MapManager(seed=12345, act_id=1)
    
    # Generate the map
    map_data = manager.generate_map()
    
    print(f"Generated map for Act {map_data.act_id}")
    print(f"Total floors: {map_data.floor_count}")
    print()
    
    # Print floor information
    for floor in range(map_data.floor_count):
        floor_nodes = map_data.get_floor(floor)
        if floor_nodes:
            print(f"Floor {floor}: {len(floor_nodes)} nodes")
            for node in floor_nodes:
                print(f"  Position {node.position}: {node.room_type.value}")
                print(f"    Up: {node.connections_up}")
        else:
            print(f"Floor {floor}: (empty)")
    
    print()
    return map_data, manager


def test_path_selection(manager):
    """Test path selection from the starting position."""
    print("=" * 60)
    print("Test 2: Path Selection")
    print("=" * 60)
    
    # Start at floor 0, position 0
    manager.map_data.set_current_position(0, 0)
    
    print(f"Current position: Floor {manager.map_data.current_floor}, "
          f"Position {manager.map_data.current_position}")
    print()
    
    # Get available moves
    available = manager.get_available_moves()
    print(f"Available moves from current position: {len(available)}")
    for node in available:
        print(f"  -> Floor {node.floor}, Position {node.position}: {node.room_type.value}")
    
    print()
    
    # Simulate moving to a node
    if available:
        target = available[0]
        print(f"Moving to: Floor {target.floor}, Position {target.position}")
        room = manager.move_to_node(target.floor, target.position)
        print(f"Created room: {type(room).__name__}")
        print(f"New position: Floor {manager.map_data.current_floor}, "
              f"Position {manager.map_data.current_position}")
    
    print()


def test_room_type_distribution():
    """Test room type distribution to verify probabilities."""
    print("=" * 60)
    print("Test 3: Room Type Distribution")
    print("=" * 60)
    
    # Generate multiple maps to check distribution
    num_runs = 100
    room_type_counts = {room_type: 0 for room_type in RoomType}
    
    for i in range(num_runs):
        manager = MapManager(seed=i, act_id=1)
        map_data = manager.generate_map()
        
        # Count room types (excluding fixed floors)
        for floor in range(1, 8):  # Floors 1-7 (random floors in first half)
            for node in map_data.get_floor(floor):
                room_type_counts[node.room_type] += 1
        
        for floor in range(9, 14):  # Floors 9-13 (random floors in second half)
            for node in map_data.get_floor(floor):
                room_type_counts[node.room_type] += 1
    
    # Calculate percentages
    total = sum(room_type_counts.values())
    print(f"Total random rooms counted: {total}")
    print()
    print("Room type distribution:")
    for room_type, count in room_type_counts.items():
        if count > 0:
            percentage = (count / total) * 100
            print(f"  {room_type.value}: {count} ({percentage:.1f}%)")
    
    print()


def test_fixed_floors():
    """Test that fixed floors have correct room types."""
    print("=" * 60)
    print("Test 4: Fixed Floor Types")
    print("=" * 60)
    
    manager = MapManager(seed=999, act_id=1)
    map_data = manager.generate_map()
    
    expected_types = {
        0: RoomType.MONSTER,
        8: RoomType.TREASURE,
        14: RoomType.REST,
        15: RoomType.BOSS,
    }
    
    print("Checking fixed floor types:")
    for floor, expected_type in expected_types.items():
        floor_nodes = map_data.get_floor(floor)
        if floor_nodes:
            all_correct = all(node.room_type == expected_type for node in floor_nodes)
            status = "✓" if all_correct else "✗"
            print(f"  {status} Floor {floor}: {expected_type.value}")
            if not all_correct:
                for node in floor_nodes:
                    print(f"      Found: {node.room_type.value} at position {node.position}")
    
    print()


def test_connections():
    """Test that all nodes have valid connections."""
    print("=" * 60)
    print("Test 5: Connection Validation")
    print("=" * 60)
    
    manager = MapManager(seed=777, act_id=1)
    map_data = manager.generate_map()
    
    all_valid = True
    
    for floor in range(map_data.floor_count):
        floor_nodes = map_data.get_floor(floor)
        
        for node in floor_nodes:
            # Check that connections up point to valid nodes
            for up_pos in node.connections_up:
                if floor + 1 < map_data.floor_count:
                    next_floor = map_data.get_floor(floor + 1)
                    if up_pos >= len(next_floor):
                        print(f"✗ Invalid up connection at Floor {floor}, "
                              f"Position {node.position}: {up_pos}")
                        all_valid = False
    
    if all_valid:
        print("✓ All connections are valid")
    
    print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Map System Test Suite" + " " * 28 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        # Test 1: Map generation
        map_data, manager = test_map_generation()
        
        # Test 2: Path selection
        test_path_selection(manager)
        
        # Test 3: Room type distribution
        test_room_type_distribution()
        
        # Test 4: Fixed floors
        test_fixed_floors()
        
        # Test 5: Connections
        test_connections()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())