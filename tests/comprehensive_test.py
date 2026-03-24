"""
Test map generation with multiple seeds to verify constraint enforcement.
"""
from map.map_manager import MapManager
from utils.types import RoomType


def test_all_constraints(seed: int):
    """Test all map generation constraints with a specific seed."""
    mm = MapManager(seed=seed, act_id=1)
    mm.generate_map()
    nodes = mm.map_data.nodes

    # Constraint 1: Floor 0 is NEO
    assert nodes[0][0].room_type == RoomType.NEO, "Floor 0 is not NEO"

    # Constraint 2: Floor 9 (index 9) is TREASURE
    floor_9_types = {n.room_type for n in nodes[9]}
    assert RoomType.TREASURE in floor_9_types, "Floor 9 doesn't have TREASURE room"

    # Constraint 3: Floor 15 (index 15) is REST
    floor_15_types = {n.room_type for n in nodes[15]}
    assert RoomType.REST in floor_15_types, "Floor 15 doesn't have REST room"

    # Constraint 4: Floors 2-4 don't have ELITE or REST
    for f in range(2, 5):
        floor_types = {n.room_type for n in nodes[f]}
        assert RoomType.ELITE not in floor_types, f"Floor {f} has ELITE (not allowed in first 5)"
        assert RoomType.REST not in floor_types, f"Floor {f} has REST (not allowed in first 5)"

    # Constraint 5: Floor 14 doesn't have REST
    floor_14_types = {n.room_type for n in nodes[14]}
    assert RoomType.REST not in floor_14_types, "Floor 14 has REST (not allowed)"

    # Constraint 6: No consecutive ELITE/REST/MERCHANT
    for f in range(1, len(nodes)):
        prev_types = {n.room_type for n in nodes[f - 1]}
        curr_types = {n.room_type for n in nodes[f]}

        for problem_type in {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}:
            assert not (
                problem_type in prev_types and problem_type in curr_types
            ), f"Consecutive {problem_type.name} on floors {f - 1} and {f}"
