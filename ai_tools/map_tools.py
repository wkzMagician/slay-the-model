"""
Map tools for AI decision making.
Provides AI-friendly map data and formatting.
"""
from typing import Dict
from map.map_manager import MapManager


def get_map_context_for_ai(map_manager: MapManager) -> Dict:
    """
    Get complete map context for AI decision making.
    
    This function provides a comprehensive view of the game map in an
    AI-friendly format, including both visual (ASCII) and structured (JSON)
    representations, plus metadata about available moves.
    
    Args:
        map_manager: The MapManager instance containing the current game map
        
    Returns:
        Dict containing:
        - current_floor: Current floor number (int)
        - current_position: Current position index on current floor (int)
        - map_ascii: ASCII string representation of the full map
        - map_json: Structured JSON data with complete map structure
        - available_moves: List of available next moves with detailed metadata
          Each move includes:
            - index: Position in the available moves list (0-based)
            - floor: Target floor number
            - position: Target position on that floor
            - room_type: Type of room (string enum value)
            - risk_level: Risk level estimate (NONE, LOW, MEDIUM, HIGH, VERY_HIGH, RANDOM)
            - reward_level: Reward level estimate (NONE, HEAL, SHOP, MEDIUM, HIGH, VERY_HIGH, RANDOM)
    """
    # Get AI-friendly map data from map manager
    return map_manager.get_map_for_ai()


def format_map_ascii(map_manager: MapManager) -> str:
    """
    Generate ASCII representation of the map.
    
    This provides a visual representation similar to what a human player would see,
    which can help AI understand the spatial relationships between nodes.
    
    Args:
        map_manager: The MapManager instance
        
    Returns:
        String containing ASCII map representation
    """
    return map_manager._format_map_ascii()


def format_map_json(map_manager: MapManager) -> Dict:
    """
    Generate structured JSON representation of the map.
    
    This provides precise, machine-readable data about the map structure,
    including all nodes, their types, and connections.
    
    Args:
        map_manager: The MapManager instance
        
    Returns:
        Dict containing:
        - structure: List of floors, each floor is a list of nodes
        - total_floors: Total number of floors
        Each node includes:
        - position: Position index on the floor
        - room_type: Room type (string enum value)
        - visited: Whether this node has been visited (bool)
        - connections_up: List of position indices this node connects to on the next floor
    """
    current_floor = map_manager.map_data.current_floor
    current_position = map_manager.map_data.current_position
    
    # Get visited positions
    visited_positions = set()
    for floor in range(current_floor):
        for pos in range(len(map_manager.map_data.nodes[floor])):
            visited_positions.add((floor, pos))
    
    # Generate map structure
    map_structure = []
    for floor in range(len(map_manager.map_data.nodes)):
        floor_data = []
        for pos, node in enumerate(map_manager.map_data.nodes[floor]):
            floor_data.append({
                "position": pos,
                "room_type": node.room_type.value,
                "visited": (floor, pos) in visited_positions,
                "connections_up": list(node.connections_up)
            })
        map_structure.append(floor_data)
    
    return {
        "structure": map_structure,
        "total_floors": len(map_manager.map_data.nodes)
    }