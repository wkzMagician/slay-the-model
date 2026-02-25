"""
Debug script to understand how rooms_data is created and why fixed floors aren't working
"""
from map.map_manager import MapManager

def test_rooms_data_creation():
    """Test how rooms_data is structured"""
    mm = MapManager(seed=1, act_id=1)
    
    # Generate floor structure
    floor_sizes = mm._generate_floor_structure()
    print("=== Floor Structure ===")
    for i, size in enumerate(floor_sizes):
        print(f"Floor {i}: {size} nodes")
    
    # Generate nodes with connections
    nodes_with_connections = mm._generate_nodes_with_connections(floor_sizes)
    
    # Create rooms_data (same as in _assign_normal_act_rooms)
    total_floors = len(nodes_with_connections)
    rooms_data = []
    for floor in range(total_floors):
        for pos, node in enumerate(nodes_with_connections[floor]):
            rooms_data.append({
                'floor': floor,
                'position': pos,
                'node': node,
                'floor_size': len(nodes_with_connections[floor])
            })
    
    print("\n=== Rooms Data Before Assignment ===")
    for room_info in rooms_data:
        floor = room_info['floor']
        position = room_info['position']
        node = room_info['node']
        print(f"Floor {floor}, Position {position}: room_type = {node.room_type}")
    
    print("\n=== Testing _assign_fixed_floors ===")
    room_counts = mm._calculate_room_counts(total_floors, nodes_with_connections)
    mm._assign_fixed_floors(rooms_data, room_counts, nodes_with_connections)
    
    print("\n=== Rooms Data After Fixed Floors ===")
    for room_info in rooms_data:
        floor = room_info['floor']
        position = room_info['position']
        node = room_info['node']
        assigned = room_info.get('assigned', False)
        print(f"Floor {floor}, Position {position}: room_type = {node.room_type}, assigned = {assigned}")
    
    print("\n=== Checking Floor 9 and 15 ===")
    floor_9_rooms = [r for r in rooms_data if r['floor'] == 9]
    print(f"\nFloor 9 (index 9) has {len(floor_9_rooms)} rooms:")
    for r in floor_9_rooms:
        print(f"  Position {r['position']}: room_type = {r['node'].room_type}, assigned = {r.get('assigned', False)}")
    
    floor_15_rooms = [r for r in rooms_data if r['floor'] == 15]
    print(f"\nFloor 15 (index 15) has {len(floor_15_rooms)} rooms:")
    for r in floor_15_rooms:
        print(f"  Position {r['position']}: room_type = {r['node'].room_type}, assigned = {r.get('assigned', False)}")

if __name__ == '__main__':
    test_rooms_data_creation()