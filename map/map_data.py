"""
Map data structure containing all nodes for a single act.
"""
from typing import List
from .map_node import MapNode


class MapData:
    """
    Contains all map nodes and navigation state for a single act.
    
    The map is organized as a 2D array [floor][position], where:
    - floor: The floor number (0-15 for standard act)
    - position: The position index on that floor (variable count)
    """
    
    def __init__(self, act_id: int = 1):
        """
        Initialize map data.
        
        Args:
            act_id: The act number (default: 1)
        """
        self.act_id = act_id
        self.nodes: List[List[MapNode]] = []  # [floor][position]
        self.current_floor: int = 0
        self.current_position: int = 0
        self.visited_path: List[tuple] = []  # [(floor, position), ...] - historical path
    
    def add_floor(self, nodes: List[MapNode]):
        """
        Add a floor to the map.
        
        Args:
            nodes: List of MapNode objects for this floor
        """
        self.nodes.append(nodes)
    
    def get_node(self, floor: int, position: int) -> MapNode:
        """
        Get a node at the specified floor and position.
        
        Args:
            floor: The floor number
            position: The position index on that floor
            
        Returns:
            The MapNode at the specified location
            
        Raises:
            IndexError: If floor or position is out of range
        """
        if 0 <= floor < len(self.nodes) and 0 <= position < len(self.nodes[floor]):
            return self.nodes[floor][position]
        return None
    
    def get_floor(self, floor: int) -> List[MapNode]:
        """
        Get all nodes on a specific floor.
        
        Args:
            floor: The floor number
            
        Returns:
            List of MapNode objects on that floor
        """
        return self.nodes[floor]
    
    def get_current_node(self) -> MapNode:
        """Get the current node based on current_floor and current_position."""
        return self.get_node(self.current_floor, self.current_position)
    
    def set_current_position(self, floor: int, position: int):
        """
        Set the current position on the map.
        
        Args:
            floor: The floor number
            position: The position index on that floor
        """
        self.current_floor = floor
        self.current_position = position
        node = self.get_current_node()
        if node:
            node.visited = True
        # Record this position in the visited path
        self.visited_path.append((floor, position))
    
    def is_on_visited_path(self, floor: int, position: int) -> bool:
        """
        Check if a node is on the historical visited path.
        
        Args:
            floor: The floor number
            position: The position index on that floor
            
        Returns:
            True if the node is on the visited path
        """
        return (floor, position) in self.visited_path
    
    @property
    def floor_count(self) -> int:
        """Get the total number of floors."""
        return len(self.nodes)
    
    @property
    def is_complete(self) -> bool:
        """Check if the current floor is the boss floor (floor 15)."""
        return self.current_floor == 15  # Boss is on floor 15 (16th floor)