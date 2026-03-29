from engine.game_state import game_state
from map.map_manager import MapManager
from map.map_node import MapNode
from utils.types import RoomType


def test_map_ascii_shows_index_row_nodes_and_connection_lines():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [
            MapNode(0, 0, RoomType.MONSTER, connections_up=[0, 2]),
            MapNode(0, 1, RoomType.ELITE, connections_up=[1]),
        ],
        [
            MapNode(1, 0, RoomType.REST),
            MapNode(1, 1, RoomType.MONSTER),
            MapNode(1, 2, RoomType.TREASURE),
        ],
    ]
    manager.map_data.set_current_position(0, 0)
    game_state.current_floor = 0
    game_state.current_act = 1

    rendered = manager._format_map_ascii()
    lines = rendered.splitlines()

    assert any("0" in line and "1" in line for line in lines)
    assert any("[*M]" in line and "[ E]" in line for line in lines)
    assert any("/" in line or "\\" in line or "|" in line or "-" in line for line in lines)


def test_map_ascii_centers_single_node_floor_in_middle_slot():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [MapNode(0, 0, RoomType.MONSTER, connections_up=[0, 1, 2])],
        [
            MapNode(1, 0, RoomType.REST),
            MapNode(1, 1, RoomType.MONSTER),
            MapNode(1, 2, RoomType.TREASURE),
        ],
    ]
    manager.map_data.set_current_position(0, 0)
    game_state.current_floor = 0
    game_state.current_act = 1

    rendered = manager._format_map_ascii()
    lines = rendered.splitlines()
    node_line = next(line for line in lines if "[*M]" in line)

    assert node_line.index("[*M]") > len("Floor  0: ")


def test_map_ascii_uses_multiple_connection_rows_to_avoid_shared_trunks():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [
            MapNode(9, 0, RoomType.TREASURE, connections_up=[0]),
            MapNode(9, 1, RoomType.TREASURE, connections_up=[1]),
            MapNode(9, 2, RoomType.TREASURE, connections_up=[2, 3]),
        ],
        [
            MapNode(10, 0, RoomType.MONSTER),
            MapNode(10, 1, RoomType.REST),
            MapNode(10, 2, RoomType.ELITE),
            MapNode(10, 3, RoomType.MERCHANT),
        ],
    ]
    manager.map_data.set_current_position(0, 0)
    game_state.current_floor = 9
    game_state.current_act = 1

    rendered = manager._format_map_ascii()
    lines = rendered.splitlines()
    floor9_index = next(i for i, line in enumerate(lines) if line.startswith("Floor"))
    floor10_index = next(i for i in range(floor9_index + 1, len(lines)) if lines[i].startswith("Floor"))

    connection_rows = lines[floor9_index + 1:floor10_index]
    assert len(connection_rows) >= 3


def test_map_ascii_keeps_horizontal_segments_away_from_destination_row():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [
            MapNode(7, 0, RoomType.REST, connections_up=[0, 1]),
            MapNode(7, 1, RoomType.ELITE, connections_up=[1]),
            MapNode(7, 2, RoomType.MONSTER, connections_up=[2]),
            MapNode(7, 3, RoomType.MONSTER, connections_up=[3, 4]),
            MapNode(7, 4, RoomType.MONSTER, connections_up=[4]),
        ],
        [
            MapNode(8, 0, RoomType.MERCHANT),
            MapNode(8, 1, RoomType.UNKNOWN),
            MapNode(8, 2, RoomType.MONSTER),
            MapNode(8, 3, RoomType.MONSTER),
            MapNode(8, 4, RoomType.MONSTER),
        ],
    ]
    manager.map_data.set_current_position(0, 0)
    game_state.current_floor = 7
    game_state.current_act = 1

    rendered = manager._format_map_ascii()
    lines = rendered.splitlines()
    floor7_index = next(i for i, line in enumerate(lines) if line.startswith("Floor"))
    floor8_node_index = next(i for i in range(floor7_index + 1, len(lines)) if lines[i].startswith("Floor"))
    floor8_index_row_index = floor8_node_index - 1

    connection_rows = lines[floor7_index + 1:floor8_index_row_index]
    assert len(connection_rows) >= 3
    assert "-" not in connection_rows[-1]


def test_map_ascii_does_not_draw_horizontal_segment_between_adjacent_destinations():
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [
            MapNode(6, 0, RoomType.MERCHANT, connections_up=[0]),
            MapNode(6, 1, RoomType.UNKNOWN, connections_up=[2]),
            MapNode(6, 2, RoomType.MONSTER, connections_up=[3]),
        ],
        [
            MapNode(7, 0, RoomType.REST),
            MapNode(7, 1, RoomType.ELITE),
            MapNode(7, 2, RoomType.MONSTER),
            MapNode(7, 3, RoomType.MONSTER),
            MapNode(7, 4, RoomType.MONSTER),
        ],
    ]
    manager.map_data.set_current_position(0, 1)
    game_state.current_floor = 6
    game_state.current_act = 1

    rendered = manager._format_map_ascii()
    lines = rendered.splitlines()
    floor6_index = next(i for i, line in enumerate(lines) if line.startswith("Floor"))
    floor7_node_index = next(i for i in range(floor6_index + 1, len(lines)) if lines[i].startswith("Floor"))
    floor7_index_row_index = floor7_node_index - 1

    connection_rows = lines[floor6_index + 1:floor7_index_row_index]
    assert len(connection_rows) >= 5

    idx_line = lines[floor7_index_row_index]
    target_2_col = idx_line.index("2")
    target_3_col = idx_line.index("3")

    lower_rows = connection_rows[-2:]
    for row in lower_rows:
        segment = row[target_2_col:target_3_col + 1]
        assert "-" not in segment
