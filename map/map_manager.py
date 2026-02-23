"""
Map manager for generating and navigating game maps.
"""
import random
from typing import List, Dict, TYPE_CHECKING, Optional
from localization import t
from utils.types import RoomType
from .map_node import MapNode
from .map_data import MapData
from .encounter_pool import EncounterPool

from tui.print_utils import tui_print
# Avoid circular import - use TYPE_CHECKING for type hints
if TYPE_CHECKING:
    from rooms.base import Room


class MapManager:
    """
    Manages map generation and navigation for a single act.
    
    Based on Slay the Spire's map generation algorithm:
    - Each act has 17 floors (0-16)
    - Floors 0, 8, 14, 15 have fixed room types
    - Other floors have random room types with weighted probabilities
    - Each floor has 2-6 nodes
    - Nodes have 1-3 connections to adjacent floors
    """
    
    # Room type probabilities for random floors (weights)
    ROOM_TYPE_WEIGHTS = {
        RoomType.MONSTER: 53,
        RoomType.ELITE: 8,
        RoomType.REST: 12,
        RoomType.MERCHANT: 5,
        RoomType.UNKNOWN: 22,
    }
    
    def __init__(self, seed: int, act_id: int = 1, deadly_events: bool = False):
        """
        Initialize map manager.
        
        Args:
            seed: Random seed for deterministic generation
            act_id: The act number (default: 1)
            deadly_events: Whether Deadly Events modifier is active (default: False)
        """
        self.seed = seed
        self.act_id = act_id
        self.rng = random.Random(seed)
        self.map_data = MapData(act_id)
        self.deadly_events = deadly_events
        
        # Initialize encounter pool system
        self.encounter_pool = EncounterPool(seed, act_id=act_id)
        
        # Track visits to each ? room type for "bad luck protection"
        # Each increment represents a visit that didn't result in that type
        self.unknown_room_visits = {
            RoomType.MONSTER: 0,    # Starts at 10%, +10% per non-monster visit
            RoomType.MERCHANT: 0,    # Starts at 3%, +3% per non-merchant visit
            RoomType.TREASURE: 0,     # Starts at 2%, +2% (or +4%) per non-treasure visit
            RoomType.ELITE: 0,        # Starts at 20% (only with deadly_events, floor 6+), +20% per non-elite visit
        }
        
        self._tiny_chest_counter = 0
        self.relic_effects = {}
        
        # Relic effects that modify unknown room probabilities
        self._relic_effects = {
            'tiny_chest': False,
            'juzu_bracelet': False,
        }
        
        # Store floor counts per act for accurate true floor calculation
        # This is populated when maps are generated for each act
        self._act_floor_counts = {}
    
    def set_relic_effect(self, effect_name: str, enabled: bool) -> None:
        """
        Enable or disable a relic effect that modifies unknown room probabilities.
        
        Args:
            effect_name: Name of the relic effect (e.g., 'tiny_chest', 'juzu_bracelet')
            enabled: Whether the effect is active
        """
        if effect_name in self._relic_effects:
            self._relic_effects[effect_name] = enabled
    
    def generate_map(self) -> MapData:
        """
        Generate a complete map for act.
        
        Returns:
            MapData containing generated map
        """
        # Generate floor structure (number of nodes per floor)
        floor_sizes = self._generate_floor_structure()
        
        # Store floor count for this act (needed for accurate true floor display)
        self._act_floor_counts[self.act_id] = len(floor_sizes)
        
        # Generate nodes with connections
        nodes_with_connections = self._generate_nodes_with_connections(floor_sizes)
        
        # Assign room types
        self._assign_room_types(nodes_with_connections)
        
        # Store in map data
        self.map_data.nodes = nodes_with_connections
        
        return self.map_data
    
    def _generate_floor_structure(self) -> List[int]:
        """
        Generate the number of nodes for each floor.
        
        Returns:
            List of node counts for each floor
        """
        from engine.game_state import game_state
        
        if self.act_id == 4:
            return [1, 1, 1, 1, 1, 1]
        
        if self.act_id == 3 and game_state.ascension >= 20:
            floor_sizes = []
            for floor in range(19):
                if floor == 0:
                    floor_sizes.append(1)
                elif floor == 1:
                    floor_sizes.append(3)
                elif floor == 9:
                    floor_sizes.append(3)
                elif floor == 15:
                    floor_sizes.append(3)
                elif floor == 16:
                    floor_sizes.append(1)
                elif floor == 17:
                    floor_sizes.append(1)
                elif floor == 18:
                    floor_sizes.append(1)
                else:
                    floor_sizes.append(self.rng.randint(3, 5))
            return floor_sizes
        
        floor_sizes = []
        for floor in range(18):
            if floor == 0:
                floor_sizes.append(1)
            elif floor == 1:
                floor_sizes.append(3)
            elif floor == 9:
                floor_sizes.append(3)
            elif floor == 15:
                floor_sizes.append(3)
            elif floor == 16:
                floor_sizes.append(1)
            elif floor == 17:
                floor_sizes.append(1)
            else:
                floor_sizes.append(self.rng.randint(3, 5))
        
        return floor_sizes
    
    def _generate_nodes_with_connections(self, floor_sizes: List[int]) -> List[List[MapNode]]:
        """
        Generate all nodes with their connections.
        
        Args:
            floor_sizes: Number of nodes per floor
            
        Returns:
            2D array of MapNode objects with connections set
        """
        nodes: List[List[MapNode]] = []
        
        # Create nodes floor by floor
        act_start_floor = self._get_act_start_floor(self.act_id)
        for floor_in_act, size in enumerate(floor_sizes):
            true_floor = act_start_floor + floor_in_act
            floor_nodes = []
            for position in range(size):
                # Default room type, will be reassigned later
                node = MapNode(true_floor, position, RoomType.MONSTER)
                floor_nodes.append(node)
            nodes.append(floor_nodes)
        
        # Create connections between adjacent floors
        for floor in range(len(floor_sizes) - 1):
            current_floor_nodes = nodes[floor]
            next_floor_nodes = nodes[floor + 1]
            
            if not current_floor_nodes or not next_floor_nodes:
                continue
            
            # Step 1: Ensure every source node has at least one outgoing connection
            # Map each source node to at least one destination (using relative positions)
            for src_pos, src_node in enumerate(current_floor_nodes):
                dest_pos = min(src_pos * len(next_floor_nodes) // len(current_floor_nodes),
                              len(next_floor_nodes) - 1)
                src_node.add_connection_up(dest_pos)
            
            # Step 2: Ensure every destination node has at least one incoming connection
            # (may already be satisfied by Step 1, but verify and fix if not)
            for dest_pos in range(len(next_floor_nodes)):
                has_incoming = any(dest_pos in node.connections_up for node in current_floor_nodes)
                if not has_incoming:
                    src_pos = min(dest_pos * len(current_floor_nodes) // len(next_floor_nodes),
                                 len(current_floor_nodes) - 1)
                    current_floor_nodes[src_pos].add_connection_up(dest_pos)
            
            # Step 3: Add additional connections for variety (30% chance per node)
            if len(current_floor_nodes) > 1:
                for src_node in current_floor_nodes:
                    if self.rng.random() < 0.3:
                        available = [p for p in range(len(next_floor_nodes)) 
                                    if p not in src_node.connections_up]
                        if available:
                            src_node.add_connection_up(self.rng.choice(available))
        
        return nodes
    
    def _assign_room_types(self, nodes: List[List[MapNode]]):
        """
        Assign room types to all nodes based on rules.
        
        Args:
            nodes: 2D array of MapNode objects
        """
        from engine.game_state import game_state
        
        for floor in range(len(nodes)):
            for node in nodes[floor]:
                if self.act_id == 4:
                    if floor == 0:
                        node.room_type = RoomType.REST
                    elif floor == 1:
                        node.room_type = RoomType.MERCHANT
                    elif floor == 2:
                        node.room_type = RoomType.ELITE
                    elif floor == 3:
                        node.room_type = RoomType.BOSS
                    elif floor == 4:
                        node.room_type = RoomType.VICTORY
                    else:
                        node.room_type = RoomType.VICTORY
                    continue
                
                if self.act_id == 3 and game_state.ascension >= 20:
                    if floor == 16:
                        node.room_type = RoomType.BOSS
                    elif floor == 17:
                        node.room_type = RoomType.BOSS
                    elif floor == 18:
                        node.room_type = RoomType.VICTORY
                    elif floor == 0:
                        node.room_type = RoomType.NEO
                    elif floor == 1:
                        node.room_type = RoomType.MONSTER
                    elif floor == 9:
                        node.room_type = RoomType.TREASURE
                    elif floor == 15:
                        node.room_type = RoomType.REST
                    else:
                        node.room_type = self._get_random_room_type()
                    continue
                
                if self.act_id == 3:
                    if floor == 16:
                        node.room_type = RoomType.BOSS
                    elif floor == 17:
                        node.room_type = RoomType.VICTORY
                    elif floor == 0:
                        node.room_type = RoomType.NEO
                    elif floor == 1:
                        node.room_type = RoomType.MONSTER
                    elif floor == 9:
                        node.room_type = RoomType.TREASURE
                    elif floor == 15:
                        node.room_type = RoomType.REST
                    else:
                        node.room_type = self._get_random_room_type()
                    continue
                
                if floor == 0:
                    node.room_type = RoomType.NEO
                elif floor == 1:
                    node.room_type = RoomType.MONSTER
                elif floor == 9:
                    node.room_type = RoomType.TREASURE
                elif floor == 15:
                    node.room_type = RoomType.REST
                elif floor == 16:
                    node.room_type = RoomType.BOSS
                elif floor == 17:
                    node.room_type = RoomType.TREASURE
                else:
                    node.room_type = self._get_random_room_type()
    
    def _get_random_room_type(self) -> RoomType:
        """
        Get a random room type based on weighted probabilities.
        
        Returns:
            A random RoomType
        """
        room_types = list(self.ROOM_TYPE_WEIGHTS.keys())
        weights = list(self.ROOM_TYPE_WEIGHTS.values())
        
        return self.rng.choices(room_types, weights=weights, k=1)[0]

    @staticmethod
    def _normalize_relic_name(name) -> str:
        if not name:
            return ""
        return str(name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    def _get_player_relics(self):
        try:
            from engine.game_state import game_state
        except Exception:
            return ()
        player = getattr(game_state, "player", None)
        return getattr(player, "relics", ()) if player else ()

    def _player_has_relic(self, relic_key: str) -> bool:
        target = self._normalize_relic_name(relic_key)
        if not target:
            return False
        for relic in self._get_player_relics():
            if isinstance(relic, str):
                if self._normalize_relic_name(relic) == target:
                    return True
                continue
            relic_id = getattr(relic, "idstr", None)
            if relic_id and self._normalize_relic_name(relic_id) == target:
                return True
            relic_name = getattr(relic, "name", None)
            if relic_name and self._normalize_relic_name(relic_name) == target:
                return True
            relic_cls_name = relic.__class__.__name__
            if relic_cls_name and self._normalize_relic_name(relic_cls_name) == target:
                return True
        return False

    @property
    def has_tiny_chest(self) -> bool:
        return self._player_has_relic("tiny_chest") or self._player_has_relic("tinychest") or self._relic_effects.get("tiny_chest", False)

    @property
    def has_juzu_bracelet(self) -> bool:
        return self._player_has_relic("juzu_bracelet") or self._player_has_relic("juzubracelet") or self._relic_effects.get("juzu_bracelet", False)

    @property
    def has_ssserpent_head(self) -> bool:
        return self._player_has_relic("ssserpent_head") or self._player_has_relic("ssserpenthead")
    
    def get_available_moves(self) -> List[MapNode]:
        """
        Get all nodes that can be moved to from the current position.
        
        Returns:
            List of MapNode objects that are reachable from current position
        """
        if self.map_data.current_floor >= len(self.map_data.nodes) - 1:
            return []
        
        current_node = self.map_data.get_current_node()
        available_nodes = []
        
        next_floor = self.map_data.current_floor + 1
        is_boss_floor = next_floor >= len(self.map_data.nodes) - 1
        
        if current_node:
            for pos in current_node.connections_up:
                if next_floor < len(self.map_data.nodes):
                    try:
                        node = self.map_data.get_node(next_floor, pos)
                        # Include all connected nodes - dead ends will be handled by game flow
                        available_nodes.append(node)
                    except IndexError:
                        pass
        
        return available_nodes
    
    def move_to_node(self, floor: int, position: int):
        """
        Move to a specific node and create the corresponding Room instance.
        
        Args:
            floor: The target floor number
            position: The position index on that floor
            
        Returns:
            Room instance for the target node
        """
        act_start_floor = self._get_act_start_floor(self.act_id)
        floor_in_act = floor - act_start_floor
        node = self.map_data.get_node(floor_in_act, position)
        
        # Create room instance based on room type
        room = self._create_room_instance(node.room_type)
        
        # Update current position
        self.map_data.set_current_position(floor_in_act, position)
        
        return room
    
    def _create_room_instance(self, room_type: RoomType):
        """
        Create a Room instance based on room type.
        
        The room content is determined by the game state, not stored in the map.
        
        Args:
            room_type: The type of room to create
            
        Returns:
            Room instance
        """
        # Import here to avoid circular dependency
        from rooms.base import Room
        from rooms.combat import CombatRoom
        from rooms.rest import RestRoom
        from rooms.shop import ShopRoom
        from rooms.treasure import TreasureRoom
        from rooms.event import EventRoom
        from rooms.victory import VictoryRoom
        from engine.game_state import game_state
        
        if room_type == RoomType.MONSTER:
            # Get monster encounter from encounter pool
            enemies, encounter_name = self.encounter_pool.get_normal_encounter(
                floor=self.map_data.current_floor,
                encounter_count=game_state.normal_encounters_fought,
                encounter_history=game_state.encounter_history,
            )
            return CombatRoom(enemies=enemies, encounter_name=encounter_name)
        
        elif room_type == RoomType.ELITE:
            # Get elite encounter from encounter pool
            enemies, encounter_name = self.encounter_pool.get_elite_encounter(
                floor=self.map_data.current_floor,
                last_elite=game_state.elite_history[-1] if game_state.elite_history else None
            )
            return CombatRoom(enemies=enemies, room_type=RoomType.ELITE, encounter_name=encounter_name)
        
        elif room_type == RoomType.BOSS:
            # Boss combat room - fight the boss!
            boss_index = 0
            if self.act_id == 3 and game_state.ascension >= 20:
                boss_index = 0 if self.map_data.current_floor == 16 else 1
            enemies, encounter_name = self.encounter_pool.get_boss_encounter(
                floor=self.map_data.current_floor,
                boss_index=boss_index,
            )
            return CombatRoom(enemies=enemies, room_type=RoomType.BOSS, encounter_name=encounter_name)
        
        elif room_type == RoomType.REST:
            return RestRoom()
        
        elif room_type == RoomType.MERCHANT:
            return ShopRoom()
        
        elif room_type == RoomType.TREASURE:
            is_boss = self.map_data.current_floor == 17 and self.act_id < 3
            return TreasureRoom(is_boss=is_boss)
        
        elif room_type == RoomType.EVENT:
            return EventRoom()
        
        elif room_type == RoomType.VICTORY:
            return VictoryRoom()
        
        elif room_type == RoomType.UNKNOWN:
            # Resolve unknown room type
            actual_type = self._resolve_unknown_type(self.map_data.current_floor)
            return self._create_room_instance(actual_type)
        
        else:
            # Fallback to EventRoom for unknown types
            return EventRoom()
    
    def _get_floor_counts_for_acts(self) -> Dict[int, int]:
        """
        Get floor counts for all acts.
        
        For acts that haven't been generated yet, estimate based on ascension.
        
        Returns:
            Dict mapping act_id -> floor_count
        """
        from engine.game_state import game_state
        
        # Start with actual floor counts from generated maps
        floor_counts = self._act_floor_counts.copy()
        
        # Fill in missing acts with estimates based on ascension
        # Only estimate for acts before current act (future acts not yet generated)
        for act_id in range(1, game_state.current_act + 1):
            if act_id not in floor_counts:
                # Estimate floor count based on act and ascension
                if act_id == 3 and game_state.ascension >= 20:
                    floor_counts[act_id] = 19
                elif act_id == 4:
                    floor_counts[act_id] = 6
                else:
                    floor_counts[act_id] = 18  # Default for acts 1-2 and normal act 3
        
        return floor_counts
    
    def _get_max_floor_for_acts(self) -> Dict[int, int]:
        """
        Get maximum floor number for each act.
        
        Since floors are 0-indexed, max floor = floor_count - 1.
        
        Returns:
            Dict mapping act_id -> max_floor_number
        """
        floor_counts = self._get_floor_counts_for_acts()
        return {act_id: count - 1 for act_id, count in floor_counts.items()}
    
    def _get_act_start_floor(self, act_id: int) -> int:
        """
        Calculate the true floor number where an act starts.
        
        Sums up all floors from previous acts.
        
        Args:
            act_id: The act number (1-4)
            
        Returns:
            The true floor number where this act begins
        """
        floor_counts = self._get_max_floor_for_acts()
        
        # Sum all floors from acts before this one
        start_floor = 0
        for prev_act in range(1, act_id):
            start_floor += floor_counts.get(prev_act, 18)
        
        return start_floor
    
    def display_map_for_human(self):
        """
        Display to map in a human-friendly format.
        
        Design principles:
        - Fixed node width: [?M] (4 chars) for consistent alignment
        - Each node shows outgoing connections below: / (left), | (center), \\ (right)
        - Max 3 outgoing and 3 incoming connections per node
        """
        from engine.game_state import game_state
        
        tui_print("\n" + "="*60)
        # Use true_floor from game_state for accurate display across acts
        current_floor = game_state.current_floor
        act_num = game_state.current_act
        tui_print(f"MAP VIEW - Act {act_num} (Floor {current_floor})")
        tui_print("="*60)
        
        # Debug: show internal state
        act_start_floor = self._get_act_start_floor(self.act_id)
        tui_print(f"DEBUG: self.act_id={self.act_id}, act_start_floor={act_start_floor}")
        tui_print(f"DEBUG: self._act_floor_counts={self._act_floor_counts}")
        tui_print(f"DEBUG: current_floor={current_floor}, floor_in_act={game_state.floor_in_act}")
        
        # Get available moves
        available_moves = self.get_available_moves()
        available_positions = {(node.floor, node.position) for node in available_moves}
        
        # Get current position
        current_position = self.map_data.current_position
        
        # Get visited nodes (historical path taken)
        visited_positions = {
            (act_start_floor + floor_in_act, pos)
            for floor_in_act, pos in self.map_data.visited_path
        }
        
        # Legend
        tui_print("\nLegend:")
        tui_print("  [M]=Monster  [E]=Elite  [$]=Merchant  [?]=Event")
        tui_print("  [R]=Rest     [T]=Treasure  [B]=Boss  [N]=Neo")
        tui_print("  *=Current   >=Available   ^=Visited")
        tui_print("  Connections: /=left  |=center  \\=right")
        tui_print()
        
        # Calculate true floor starting point for this act
        act_start_floor = self._get_act_start_floor(self.act_id)
        
        # Display map floor by floor
        for floor in range(len(self.map_data.nodes)):
            floor_nodes = self.map_data.nodes[floor]
            if not floor_nodes:
                continue
            
            next_floor_nodes = self.map_data.nodes[floor + 1] if floor + 1 < len(self.map_data.nodes) else []
            num_srcs = len(floor_nodes)
            num_dests = len(next_floor_nodes)
            
            # Calculate true floor for display
            true_floor = act_start_floor + floor
            
            # Display floor nodes with fixed width (5 chars total)
            # Format: [ M ] normal, [*M ] current, [>M ] available, [^M ] visited
            line = f"Floor {true_floor:2d}: "
            for pos, node in enumerate(floor_nodes):
                symbol = self._get_room_symbol(node.room_type)
                
                if true_floor == current_floor and pos == current_position:
                    # Current position: [*M ]
                    node_str = f"[*{symbol} ]"
                elif (true_floor, pos) in available_positions:
                    # Available: [>M ]
                    node_str = f"[>{symbol} ]"
                elif (true_floor, pos) in visited_positions:
                    # Visited: [^M ] - shows visited status and room type
                    node_str = f"[^{symbol} ]"
                else:
                    # Normal unvisited: [ M ]
                    node_str = f"[ {symbol} ]"
                
                line += node_str
            
            tui_print(line)
            
            # Display connection lines to next floor
            if next_floor_nodes:
                # Build connection display: 5 chars per source node
                # Position connectors to align with the room symbol (position 2 in [?M ])
                conn_line = "           "  # Match "Floor XX: " prefix
                
                for src_idx, src_node in enumerate(floor_nodes):
                    if not src_node.connections_up:
                        # No connections - add empty space (5 chars)
                        conn_line += "     "
                        continue
                    
                    # Determine which directions this node connects to
                    # based on relative positions
                    connects_left = False
                    connects_center = False
                    connects_right = False
                    
                    for dest_pos in src_node.connections_up:
                        # Find the array index for this destination
                        dest_idx = None
                        for i, n in enumerate(next_floor_nodes):
                            if n.position == dest_pos:
                                dest_idx = i
                                break
                        
                        if dest_idx is not None:
                            # Calculate relative position
                            src_rel = src_idx / max(num_srcs - 1, 1) if num_srcs > 1 else 0.5
                            dest_rel = dest_idx / max(num_dests - 1, 1) if num_dests > 1 else 0.5
                            
                            diff = dest_rel - src_rel
                            if diff < -0.15:
                                connects_left = True
                            elif diff > 0.15:
                                connects_right = True
                            else:
                                connects_center = True
                    
                    # Build connection display for this node (5 chars)
                    # Connectors at positions 1-3 to align with room symbol
                    if connects_left and connects_center and connects_right:
                        conn_line += "/|\\  "
                    elif connects_left and connects_center:
                        conn_line += "/|   "
                    elif connects_center and connects_right:
                        conn_line += " |\\  "
                    elif connects_left and connects_right:
                        conn_line += "/ \\  "
                    elif connects_left:
                        conn_line += "/    "
                    elif connects_center:
                        conn_line += " |   "
                    elif connects_right:
                        conn_line += "  \\  "
                    else:
                        conn_line += "     "
                
                # Only print connection line if there are actual connections
                if any(c != " " for c in conn_line[11:]):
                    tui_print(conn_line)
        
        tui_print("\n" + "="*60)
        tui_print()
    
    def get_map_for_ai(self) -> Dict:
        """
        Get AI-friendly map data including both ASCII and JSON formats.
        
        Returns:
            Dict containing:
            - current_floor: Current floor number
            - current_position: Current position index
            - map_ascii: ASCII representation of map
            - map_json: Structured JSON data
            - available_moves: List of available next moves with metadata
        """
        from engine.game_state import game_state
        
        available_moves = self.get_available_moves()
        
        # Get current position - use true_floor for accurate display
        current_floor = game_state.current_floor
        current_position = self.map_data.current_position
        
        # Get visited nodes (historical path taken)
        visited_positions = set(self.map_data.visited_path)
        
        # Calculate true floor starting point for this act
        act_start_floor = self._get_act_start_floor(self.act_id)
        
        # Generate available moves data
        available_moves_data = []
        for idx, node in enumerate(available_moves):
            # Use true floor for AI-friendly display
            true_floor = node.floor
            available_moves_data.append({
                "index": idx,
                "floor": true_floor,
                "position": node.position,
                "room_type": node.room_type.value,
                "risk_level": self._get_risk_level(node.room_type),
                "reward_level": self._get_reward_level(node.room_type)
            })
        
        # Generate map structure JSON
        map_structure = []
        for floor in range(len(self.map_data.nodes)):
            floor_data = []
            for pos, node in enumerate(self.map_data.nodes[floor]):
                floor_data.append({
                    "position": pos,
                    "room_type": node.room_type.value,
                    "visited": (floor, pos) in visited_positions,
                    "connections_up": node.connections_up
                })
            map_structure.append(floor_data)
        
        return {
            "current_floor": current_floor,
            "current_position": current_position,
            "map_ascii": self._format_map_ascii(available_positions={(node.floor, node.position) for node in available_moves}),
            "map_json": {
                "structure": map_structure,
                "total_floors": len(self.map_data.nodes)
            },
            "available_moves": available_moves_data
        }
    
    def _get_room_symbol(self, room_type: RoomType) -> str:
        """Get display symbol for room type"""
        symbols = {
            RoomType.MONSTER: "M",
            RoomType.ELITE: "E",
            RoomType.BOSS: "B",
            RoomType.REST: "R",
            RoomType.MERCHANT: "$",
            RoomType.TREASURE: "T",
            RoomType.NEO: "N",
            RoomType.UNKNOWN: "?"
        }
        return symbols.get(room_type, "?")
    
    def _get_risk_level(self, room_type: RoomType) -> str:
        """Get risk level for room type"""
        risks = {
            RoomType.MONSTER: "MEDIUM",
            RoomType.ELITE: "HIGH",
            RoomType.BOSS: "VERY_HIGH",
            RoomType.REST: "NONE",
            RoomType.MERCHANT: "NONE",
            RoomType.TREASURE: "NONE",
            RoomType.UNKNOWN: "RANDOM"
        }
        return risks.get(room_type, "UNKNOWN")
    
    def _get_reward_level(self, room_type: RoomType) -> str:
        """Get reward level for room type"""
        rewards = {
            RoomType.MONSTER: "MEDIUM",
            RoomType.ELITE: "HIGH",
            RoomType.BOSS: "VERY_HIGH",
            RoomType.REST: "HEAL",
            RoomType.MERCHANT: "SHOP",
            RoomType.TREASURE: "HIGH",
            RoomType.UNKNOWN: "RANDOM"
        }
        return rewards.get(room_type, "UNKNOWN")
    
    def _format_map_ascii(self, available_positions: Optional[set] = None) -> str:
        """
        Generate ASCII map representation.
        
        Args:
            available_positions: Set of (floor, position) tuples that are available
            
        Returns:
            ASCII string representation of map
        """
        from engine.game_state import game_state
        
        # Calculate true floor starting point for this act
        act_start_floor = self._get_act_start_floor(self.act_id)
        
        if available_positions is None:
            available_moves = self.get_available_moves()
            # Convert to true floor numbers for consistent comparison
            available_positions = {(node.floor, node.position) for node in available_moves}

        lines = []
        
        # Get act-level floor (0-17 within current act)
        current_floor_act = self.map_data.current_floor
        current_position = self.map_data.current_position
        
        # Get visited positions (use true floor numbers)
        visited_positions = set()
        for floor in range(current_floor_act):
            for pos in range(len(self.map_data.nodes[floor])):
                true_floor = act_start_floor + floor
                visited_positions.add((true_floor, pos))
        
        # Display map floor by floor
        for floor in range(len(self.map_data.nodes)):
            floor_nodes = self.map_data.nodes[floor]
            if not floor_nodes:
                continue
            
            # Calculate true floor number for display
            true_floor = act_start_floor + floor
            
            # Display floor nodes
            line = f"Floor {true_floor:2d}: "
            for pos, node in enumerate(floor_nodes):
                # Determine symbol and prefix
                symbol = self._get_room_symbol(node.room_type)
                prefix = ""
                
                # Use act-level floor for position comparison
                if floor == current_floor_act and pos == current_position:
                    prefix = "*"
                elif (true_floor, pos) in available_positions:
                    prefix = ">"
                elif (true_floor, pos) in visited_positions:
                    symbol = "X"
                
                line += f"[{prefix}{symbol}] "
            
            lines.append(line)
            
            # Display connection lines to next floor
            if floor < len(self.map_data.nodes) - 1:
                next_floor_nodes = self.map_data.nodes[floor + 1]
                if len(next_floor_nodes) > 0:
                    connection_line = "        "
                    
                    # For each position on current floor, determine connection display
                    for pos in range(len(floor_nodes)):
                        node = floor_nodes[pos]
                        if not node.connections_up:
                            connection_line += "    "
                        else:
                            # Determine which directions this node connects to
                            has_left = any(c < pos for c in node.connections_up)
                            has_center = any(c == pos for c in node.connections_up)
                            has_right = any(c > pos for c in node.connections_up)
                            
                            # Build connection string (max 3 chars)
                            conn_str = ""
                            if has_left:
                                conn_str += "\\"
                            if has_center:
                                conn_str += "|"
                            if has_right:
                                conn_str += "/"
                            
                            # Pad to 4 chars for alignment with node display
                            connection_line += conn_str.ljust(4)
                    
                    lines.append(connection_line)
        
        return "\n".join(lines)

    def get_map_text_for_human(self) -> str:
        """Get map text block for TUI display panel (no printing)."""
        from engine.game_state import game_state

        current_floor = game_state.current_floor
        act_num = game_state.current_act
        available_moves = self.get_available_moves()
        available_positions = {(node.floor, node.position) for node in available_moves}

        lines = [
            "=" * 60,
            f"MAP VIEW - Act {act_num} (Floor {current_floor})",
            "=" * 60,
            "",
            "Legend:",
            "  [M]=Monster  [E]=Elite  [$]=Merchant  [?]=Event",
            "  [R]=Rest     [T]=Treasure  [B]=Boss  [N]=Neo",
            "  *=Current   >=Available   X=Visited",
            "",
            self._format_map_ascii(available_positions),
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    def _resolve_unknown_type(self, floor: int) -> RoomType:
        """
        Determine what type an unknown room becomes when entered.
        
        Based on Slay the Spire's ? room mechanics:
        - Base chances: Monster 10%, Treasure 2%, Shop 3%, Elite 20% (with deadly_events, floor 6+)
        - Each visit that doesn't result in a type increases its chance
        - Event fills remaining probability
        - Tiny Chest relic: Every 4th ? room is Treasure (resets treasure chance)
        - Juzu Bracelet: Regular enemy combats no longer in ? rooms
        - Ssserpent Head: Gain 50 Gold on entering ? room
        
        Args:
            floor: The current floor number
            
        Returns:
            The actual RoomType for this unknown room
        """
        # Check Tiny Chest relic - every 4th ? room is Treasure
        self._tiny_chest_counter += 1
        if self.has_tiny_chest and self._tiny_chest_counter % 4 == 0:
            # Tiny Chest forces Treasure room, resets treasure visit counter
            self.unknown_room_visits[RoomType.TREASURE] = 0
            return RoomType.TREASURE
        
        # Calculate current probabilities based on visit counts
        monster_chance = 10 + (self.unknown_room_visits[RoomType.MONSTER] * 10)
        treasure_chance = 2 + (self.unknown_room_visits[RoomType.TREASURE] * (4 if self.deadly_events else 2))
        shop_chance = 3 + (self.unknown_room_visits[RoomType.MERCHANT] * 3)
        
        # Elite only appears with deadly_events modifier on floor 6+
        elite_chance = 0
        if self.deadly_events and floor >= 6:
            elite_chance = 20 + (self.unknown_room_visits[RoomType.ELITE] * 20)
        
        # Juzu Bracelet removes regular monsters from ? rooms
        if self.has_juzu_bracelet:
            monster_chance = 0
        
        # Event fills remaining probability
        total_chances = monster_chance + treasure_chance + shop_chance + elite_chance
        event_chance = 100 - total_chances
        
        # Roll for encounter type
        roll = self.rng.randint(1, 100)
        
        if roll <= monster_chance:
            chosen_type = RoomType.MONSTER
        elif roll <= monster_chance + treasure_chance:
            chosen_type = RoomType.TREASURE
        elif roll <= monster_chance + treasure_chance + shop_chance:
            chosen_type = RoomType.MERCHANT
        elif roll <= monster_chance + treasure_chance + shop_chance + elite_chance:
            chosen_type = RoomType.ELITE
        else:
            chosen_type = RoomType.EVENT  # Event
        
        # Reset visit counter for the chosen type
        self.unknown_room_visits[chosen_type] = 0
        
        # Increment visit counters for all other types
        for room_type in self.unknown_room_visits:
            if room_type != chosen_type:
                self.unknown_room_visits[room_type] += 1
        
        # Ssserpent Head effect: gain 50 Gold
        if self.has_ssserpent_head:
            from engine.game_state import game_state
            game_state.player.gold += 50
            tui_print(t("ui.ssserpent_head_gold", default="Ssserpent Head: Gained 50 gold!"))
        
        return chosen_type
