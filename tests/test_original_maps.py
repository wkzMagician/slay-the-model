"""Original JAR graph/room snapshots and the real navigation adapter."""
import gzip
import json
from pathlib import Path

import pytest

from engine.game_state import game_state
from engine.random_streams import RandomStreams, StreamRandom
from map.original_map import GridNode, generate_paths, assign_rooms, assignable
from utils.types import RoomType

REFERENCES = json.loads(gzip.decompress((Path(__file__).parent / "fixtures/original_map_vectors.json.gz").read_bytes()))


def snapshot(grid):
    return [[[node.edges, node.room_type.name if node.room_type else None,
              [parent.x for parent in node.parents]] for node in row] for row in grid]


@pytest.mark.parametrize("reference", REFERENCES, ids=lambda r: f"S{r['seed']}-act{r['act']}-A{r['ascension']}")
def test_original_jar_paths_rooms_and_normal_game_state_adapter(reference):
    rng = StreamRandom(int(reference["map_seed"]))
    grid = generate_paths(rng)
    assert rng.export_state() == reference["path_state"]
    counts = assign_rooms(grid, rng, reference["ascension"])
    assert snapshot(grid) == reference["nodes"]
    assert {kind.name: count for kind, count in counts.items()} == reference["quotas"]
    assert rng.export_state() == reference["room_state"]

    game_state.random_streams = RandomStreams(int(reference["seed"]))
    game_state.current_act = reference["act"]
    game_state.ascension = reference["ascension"]
    game_state.initialize_map()
    manager = game_state.map_manager
    assert snapshot(manager.original_grid) == reference["nodes"]
    assert manager.rng.export_state() == reference["room_state"]
    rows = manager.map_data.nodes
    assert len(rows) == (19 if reference["act"] == 3 and reference["ascension"] == 20 else 18)
    assert rows[0][0].connections_up == list(range(len(rows[1])))
    for y, original_row in enumerate(grid):
        connected = [node for node in original_row if node.edges]
        assert [node.map_x for node in rows[y + 1]] == [node.x for node in connected]
        for original, compact in zip(connected, rows[y + 1]):
            assert compact.room_type == original.room_type
            assert compact.floor == manager._get_act_start_floor(reference["act"]) + y + 1
            destinations = [rows[y + 2][index].map_x for index in compact.connections_up]
            assert destinations == original.edges
    before = game_state.random_streams.export_state()
    assert manager.get_map_text_for_human()
    assert manager.get_map_for_ai()
    assert game_state.random_streams.export_state() == before


@pytest.mark.parametrize("kind", [RoomType.MONSTER, RoomType.UNKNOWN, RoomType.REST, RoomType.ELITE, RoomType.MERCHANT])
@pytest.mark.parametrize("layout", ["unrelated_parent", "own_parent", "sibling", "unrelated_peer"])
def test_room_rules_use_actual_family_not_whole_rows(kind, layout):
    grid = [[GridNode(x, y) for x in range(7)] for y in range(15)]
    node = grid[7][3]
    parent = grid[6][3]
    parent.room_type = RoomType.MONSTER
    parent.edges = [3]
    node.parents = [parent]
    if layout == "unrelated_parent":
        grid[6][0].room_type = kind
    elif layout == "own_parent":
        parent.room_type = kind
    elif layout == "sibling":
        parent.edges.append(4)
        grid[7][4].room_type = kind
    else:
        grid[7][0].room_type = kind
    expected = not (layout == "sibling" or layout == "own_parent" and kind in
                    (RoomType.REST, RoomType.ELITE, RoomType.MERCHANT))
    assert assignable(node, kind, grid) == expected


@pytest.mark.parametrize("row", [0, 4, 5, 12, 13])
@pytest.mark.parametrize("kind", [RoomType.REST, RoomType.ELITE])
def test_original_row_limits(row, kind):
    grid = [[GridNode(x, y) for x in range(7)] for y in range(15)]
    assert assignable(grid[row][0], kind, grid) == (row >= 5 and not (row >= 13 and kind == RoomType.REST))


@pytest.mark.parametrize("relic", [None, "juzu", "tiny_chest"])
def test_generated_unknown_node_enters_real_resolver_once(monkeypatch, relic):
    from relics.global_relics.common import JuzuBracelet, TinyChest

    game_state.random_streams = RandomStreams(2)
    game_state.current_act = 1
    game_state.initialize_map()
    manager = game_state.map_manager
    game_state.player.relics = []
    if relic == "juzu":
        game_state.player.relics.append(JuzuBracelet())
    if relic == "tiny_chest":
        chest = TinyChest()
        chest.event_count = 3
        game_state.player.relics.append(chest)
    # Earliest generated '?' and its real connected predecessor path. Rooms
    # are constructed through legal moves; battles are not played/won here.
    paths = {0: []}
    target_path = None
    for row in manager.map_data.nodes[:-1]:
        next_paths = {}
        for node in row:
            if node.position not in paths:
                continue
            path = paths[node.position] + [(node.floor, node.position)]
            if node.room_type == RoomType.UNKNOWN:
                target_path = path[1:]
                break
            for destination in node.connections_up:
                next_paths.setdefault(destination, path)
        if target_path:
            break
        paths = next_paths
    assert target_path is not None
    calls = []
    original = manager._resolve_unknown_type

    def observe(floor):
        calls.append(floor)
        return original(floor)

    monkeypatch.setattr(manager, "_resolve_unknown_type", observe)
    for floor, position in target_path:
        room = manager.move_to_node(floor, position)
    assert calls == [target_path[-1][0]]
    current_node = manager.map_data.get_current_node()
    assert current_node is not None and current_node.room_type == RoomType.UNKNOWN
    assert room.room_type == (RoomType.EVENT if relic == "juzu" else RoomType.TREASURE if relic == "tiny_chest" else RoomType.MONSTER)
    assert game_state.random_streams["event"].counter == (0 if relic == "tiny_chest" else 1)


@pytest.mark.parametrize("ascension", [0, 20])
def test_fourth_act_fixed_chain_does_not_sample_map_rng(ascension):
    game_state.ascension = ascension
    game_state.current_act = 4
    game_state.random_streams = RandomStreams(42)
    game_state.initialize_map()
    assert [row[0].room_type for row in game_state.map_manager.map_data.nodes] == [
        RoomType.REST, RoomType.MERCHANT, RoomType.ELITE, RoomType.BOSS, RoomType.VICTORY]
    assert game_state.map_manager.rng.counter == 0
