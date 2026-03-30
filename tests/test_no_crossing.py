"""Map generation should preserve left-to-right path ordering between floors."""

from map.map_manager import MapManager


def _find_crossing(nodes):
    for floor in range(len(nodes) - 1):
        connections = []
        for node in nodes[floor]:
            for up_pos in node.connections_up:
                connections.append((node.position, up_pos))

        for i in range(len(connections)):
            src_a, dst_a = connections[i]
            for j in range(i + 1, len(connections)):
                src_b, dst_b = connections[j]
                if src_a < src_b and dst_a > dst_b:
                    return floor, (src_a, dst_a), (src_b, dst_b)
                if src_a > src_b and dst_a < dst_b:
                    return floor, (src_a, dst_a), (src_b, dst_b)
    return None


def test_map_generation_has_no_crossing_connections_for_regression_seed():
    manager = MapManager(seed=0, act_id=1)
    map_data = manager.generate_map()

    assert _find_crossing(map_data.nodes) is None


def test_map_generation_has_no_crossing_connections_across_multiple_seeds():
    for seed in range(50):
        manager = MapManager(seed=seed, act_id=1)
        map_data = manager.generate_map()
        assert _find_crossing(map_data.nodes) is None, f"crossing found for seed {seed}"
