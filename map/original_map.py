"""Normal-mode fixed-grid paths and room assignment from the fixed original.

Keep grid coordinates/parent order here; MapManager adapts connected nodes to
the project's compact positions and synthetic entry/boss/exit rows.
"""
from dataclasses import dataclass, field

from engine.random_streams import StreamRandom
from utils.compatible_random import float32, java_round_float
from utils.types import RoomType


@dataclass(eq=False)
class GridNode:
    x: int
    y: int
    edges: list[int] = field(default_factory=list)
    parents: list["GridNode"] = field(default_factory=list)
    room_type: RoomType | None = None


def common_ancestor(a: GridNode, b: GridNode, depth: int = 5) -> GridNode | None:
    # The original bytecode compares node1.x to node2.y, including this quirk.
    left, right = (a, b) if a.x < b.y else (b, a)
    for _ in range(a.y, max(-1, a.y - depth - 1), -1):
        if not left.parents or not right.parents:
            return None
        left = max(left.parents, key=lambda n: n.x)
        right = min(right.parents, key=lambda n: n.x)
        if left is right:
            return left
    return None


def generate_paths(rng: StreamRandom) -> list[list[GridNode]]:
    grid = [[GridNode(x, y) for x in range(7)] for y in range(15)]

    def grow(x: int, y: int) -> None:
        current = grid[y][x]
        if y == 14:
            if 3 not in current.edges:
                current.edges.append(3)  # original boss edge (3,16)
            return
        low, high = (0, 1) if x == 0 else (-1, 0) if x == 6 else (-1, 1)
        next_x = x + rng.random_int(low, high)
        target = grid[y + 1][next_x]
        for parent in target.parents:
            if parent is current:
                continue
            ancestor = common_ancestor(parent, current)
            if ancestor is None or y + 1 - ancestor.y >= 3:
                continue
            if target.x > current.x:
                next_x = max(0, x + rng.random_int(-1, 0))
            elif target.x == current.x:
                next_x = x + rng.random_int(-1, 1)
                if next_x > 6:
                    next_x = x - 1
                elif next_x < 0:
                    next_x = x + 1
            else:
                next_x = min(6, x + rng.random_int(0, 1))
            target = grid[y + 1][next_x]
        if x > 0 and grid[y][x - 1].edges:
            next_x = max(next_x, max(grid[y][x - 1].edges))
        if x < 6 and grid[y][x + 1].edges:
            next_x = min(next_x, min(grid[y][x + 1].edges))
        if next_x not in current.edges:
            current.edges.append(next_x)
            current.edges.sort()
        # Original addParent retains duplicates, even for an existing edge.
        grid[y + 1][next_x].parents.append(current)
        grow(next_x, y + 1)

    first_start = -1
    for path in range(6):
        start = rng.random_int(6)
        if path == 0:
            first_start = start
        while path == 1 and start == first_start:
            start = rng.random_int(6)
        grow(start, 0)
    seen: set[int] = set()
    for node in grid[0]:
        kept = []
        for target in node.edges:
            if target not in seen:
                kept.append(target)
            seen.add(target)
        node.edges[:] = kept
    return grid


def room_counts(grid: list[list[GridNode]], ascension: int) -> dict[RoomType, int]:
    # AbstractDungeon.generateMap counts outgoing nodes except original y13,
    # before assigning the fixed rows. This differs from the unassigned count.
    count = sum(bool(n.edges) for row in grid for n in row if n.y != 13)
    elite = float32(float32(count) * float32(0.08))
    if ascension >= 1:
        elite = float32(elite * float32(1.6))
    return {
        RoomType.MERCHANT: java_round_float(float32(count) * float32(0.05)),
        RoomType.REST: java_round_float(float32(count) * float32(0.12)),
        RoomType.ELITE: java_round_float(elite),
        RoomType.UNKNOWN: java_round_float(float32(count) * float32(0.22)),
    }


def assignable(node: GridNode, kind: RoomType, grid: list[list[GridNode]]) -> bool:
    if node.y <= 4 and kind in (RoomType.REST, RoomType.ELITE):
        return False
    if node.y >= 13 and kind == RoomType.REST:
        return False
    if node.y == 0:
        return True
    if kind in (RoomType.REST, RoomType.TREASURE, RoomType.MERCHANT, RoomType.ELITE):
        if any(parent.room_type == kind for parent in node.parents):
            return False
    if kind in (RoomType.REST, RoomType.MONSTER, RoomType.UNKNOWN, RoomType.ELITE, RoomType.MERCHANT):
        for parent in node.parents:
            for x in parent.edges:
                sibling = grid[node.y][x]
                if sibling is not node and sibling.room_type == kind:
                    return False
    return True


def assign_rooms(grid: list[list[GridNode]], rng: StreamRandom, ascension: int) -> dict[RoomType, int]:
    counts = room_counts(grid, ascension)
    rooms = [kind for kind, count in counts.items() for _ in range(count)]
    for y, kind in ((14, RoomType.REST), (0, RoomType.MONSTER), (8, RoomType.TREASURE)):
        for node in grid[y]:
            node.room_type = kind
    unassigned = sum(bool(n.edges) and n.room_type is None for row in grid for n in row)
    rooms.extend([RoomType.MONSTER] * max(0, unassigned - len(rooms)))
    # RoomTypeAssigner uses Collections.shuffle(roomList, rng.random): direct
    # XS128 nextInt(bound), with no wrapper counter/child seed consumption.
    for end in range(len(rooms), 1, -1):
        index = rng.raw.next_int(end)
        rooms[end - 1], rooms[index] = rooms[index], rooms[end - 1]
    for row in grid:
        for node in row:
            if not node.edges or node.room_type is not None:
                continue
            for index, kind in enumerate(rooms):
                if assignable(node, kind, grid):
                    node.room_type = rooms.pop(index)
                    break
    for row in grid:
        for node in row:
            if node.edges and node.room_type is None:
                node.room_type = RoomType.MONSTER
    return counts
