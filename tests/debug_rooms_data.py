"""Inspect original-grid quotas and the compact navigation adapter."""
from map.map_manager import MapManager
from map.original_map import generate_paths, room_counts, assign_rooms
from engine.random_streams import StreamRandom


def test_rooms_data_creation():
    """Print graph coordinates, fixed rooms and generated room quotas."""
    rng = StreamRandom(1)
    grid = generate_paths(rng)
    print("=== Original Grid / Quotas ===")
    print({kind.name: count for kind, count in room_counts(grid, 0).items()})
    assign_rooms(grid, rng, 0)
    for row in grid:
        print([(n.x, n.y, n.room_type.name if n.room_type else None, n.edges)
               for n in row if n.edges])
    print("=== Compact Navigation Rows ===")
    manager = MapManager(seed=1)
    manager.generate_map()
    for row, nodes in enumerate(manager.map_data.nodes):
        print(row, [(n.position, n.map_x, n.room_type.name, n.connections_up) for n in nodes])


if __name__ == "__main__":
    test_rooms_data_creation()
