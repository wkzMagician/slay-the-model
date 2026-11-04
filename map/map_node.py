"""
Map node representing a single location on the map.
"""
from typing import List, Optional
from utils.types import RoomType


class MapNode:
    """A single node on game map representing a room location."""
    
    def __init__(
        self,
        floor: int,
        position: int,
        room_type: RoomType,
        connections_up: Optional[List[int]] = None,
        visited: bool = False
    ):
        """
        Initialize a map node.
        
        Args:
            floor: The floor number (0-based)
            position: The position index on this floor (0-based)
            room_type: The type of room at this node
            connections_up: List of node positions above that connect to this node
            visited: Whether this node has been visited
        """
        self.floor = floor
        self.position = position
        self.room_type = room_type
        self.connections_up = connections_up or []
        self.visited = visited
        self.map_x: int | None = None  # original grid column, before compacting
    
    def add_connection_up(self, position: int):
        """Add an upward connection to the specified node position."""
        if position not in self.connections_up:
            self.connections_up.append(position)
    
    def __repr__(self):
        return f"MapNode(floor={self.floor}, pos={self.position}, type={self.room_type.value})"
