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
    MAP_SLOT_LAYOUTS = {
        1: [2],
        2: [1, 3],
        3: [0, 2, 4],
        4: [0, 1, 3, 4],
        5: [0, 1, 2, 3, 4],
    }
    MAP_SLOT_WIDTH = 8
    
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
            effect_name: Name of relic effect (e.g., 'tiny_chest', 'juzu_bracelet')
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
        Generate number of nodes for each floor.
        
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
                    src_pos = self._find_non_crossing_source_for_destination(
                        current_floor_nodes=current_floor_nodes,
                        dest_pos=dest_pos,
                        next_floor_size=len(next_floor_nodes),
                    )
                    if src_pos is not None:
                        current_floor_nodes[src_pos].add_connection_up(dest_pos)
            
            # Step 3: Add additional connections for variety (30% chance per node)
            if len(current_floor_nodes) > 1:
                for src_pos, src_node in enumerate(current_floor_nodes):
                    if self.rng.random() < 0.3:
                        available = [p for p in range(len(next_floor_nodes)) 
                                    if p not in src_node.connections_up
                                    and not self._would_connection_cross(
                                        current_floor_nodes=current_floor_nodes,
                                        src_pos=src_pos,
                                        dest_pos=p,
                                    )]
                        if available:
                            src_node.add_connection_up(self.rng.choice(available))
        
        return nodes

    def _would_connection_cross(
        self,
        current_floor_nodes: List[MapNode],
        src_pos: int,
        dest_pos: int,
    ) -> bool:
        """Return True when adding this edge would reverse left-to-right order."""
        for other_src_pos, other_node in enumerate(current_floor_nodes):
            if other_src_pos == src_pos:
                continue
            for other_dest_pos in other_node.connections_up:
                if other_src_pos < src_pos and other_dest_pos > dest_pos:
                    return True
                if other_src_pos > src_pos and other_dest_pos < dest_pos:
                    return True
        return False

    def _find_non_crossing_source_for_destination(
        self,
        current_floor_nodes: List[MapNode],
        dest_pos: int,
        next_floor_size: int,
    ) -> Optional[int]:
        """Pick the closest source that can connect to dest_pos without crossing."""
        current_floor_size = len(current_floor_nodes)
        ideal_src_pos = min(
            dest_pos * current_floor_size // next_floor_size,
            current_floor_size - 1,
        )
        candidate_positions = sorted(
            range(current_floor_size),
            key=lambda pos: (abs(pos - ideal_src_pos), pos),
        )
        for src_pos in candidate_positions:
            if not self._would_connection_cross(current_floor_nodes, src_pos, dest_pos):
                return src_pos
        return None
    
    def _assign_room_types(self, nodes: List[List[MapNode]]):
        """
        Assign room types to all nodes based on rules.
        
        Algorithm:
        1. Calculate total room counts for each type based on probabilities
        2. Assign fixed floor types (floor 1=M, 9=T, 15=R)
        3. Assign remaining rooms respecting constraints:
           - No elite/rest in first 5 floors
           - No rest on floor 14
           - No consecutive elite/rest/shop rooms
           - Floor 8 (floor index) rooms have diverse types (for floor 9 treasure)
        
        Args:
            nodes: 2D array of MapNode objects
        """
        from engine.game_state import game_state
        
        total_floors = len(nodes)
        
        # Handle special cases for Act 4 and Act 3 with ascension 20+
        if self.act_id == 4:
            self._assign_act4_rooms(nodes)
            return
        
        if self.act_id == 3 and game_state.ascension >= 20:
            self._assign_act3_asc20_rooms(nodes)
            return
        
        if self.act_id == 3:
            self._assign_act3_rooms(nodes)
            return
        
        # Normal act (1 or 2) room assignment
        self._assign_normal_act_rooms(nodes)
    
    def _assign_act4_rooms(self, nodes: List[List[MapNode]]):
        """Assign rooms for Act 4 (fixed pattern)"""
        for floor in range(len(nodes)):
            for node in nodes[floor]:
                if floor == 0:
                    node.room_type = RoomType.REST
                elif floor == 1:
                    node.room_type = RoomType.MERCHANT
                elif floor == 2:
                    node.room_type = RoomType.ELITE
                elif floor == 3:
                    node.room_type = RoomType.BOSS
                else:
                    node.room_type = RoomType.VICTORY
    
    def _assign_act3_asc20_rooms(self, nodes: List[List[MapNode]]):
        """Assign rooms for Act 3 with ascension 20+"""
        for floor in range(len(nodes)):
            for node in nodes[floor]:
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
    
    def _assign_act3_rooms(self, nodes: List[List[MapNode]]):
        """Assign rooms for Act 3"""
        for floor in range(len(nodes)):
            for node in nodes[floor]:
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
    
    # Define fixed floor types for normal acts (1 or 2)
    FIXED_FLOOR_TYPES = {
        0: RoomType.NEO,
        1: RoomType.MONSTER,
        9: RoomType.TREASURE,
        15: RoomType.REST,
        16: RoomType.BOSS,
        17: RoomType.TREASURE,
    }
    
    def _is_fixed_floor(self, floor: int) -> bool:
        """Check if a floor has a fixed room type."""
        return floor in self.FIXED_FLOOR_TYPES
    
    def _get_fixed_room_type(self, floor: int) -> Optional[RoomType]:
        """Get the fixed room type for a floor, or None if not fixed."""
        return self.FIXED_FLOOR_TYPES.get(floor)
    
    def _assign_normal_act_rooms(self, nodes: List[List[MapNode]]):
        """
        Assign rooms for normal acts (1 or 2) with all constraints.
        
        Algorithm:
        1. Assign fixed floors first (they are immutable)
        2. Calculate room counts for remaining floors
        3. Assign remaining floors respecting all constraints
        """
        total_floors = len(nodes)
        
        # Step 1: Assign fixed floors FIRST and make them immutable
        for floor in range(total_floors):
            fixed_type = self._get_fixed_room_type(floor)
            if fixed_type:
                for node in nodes[floor]:
                    node.room_type = fixed_type
        
        # Step 2: Create a list of only non-fixed rooms for assignment
        rooms_data = []
        for floor in range(total_floors):
            # Skip fixed floors entirely
            if self._is_fixed_floor(floor):
                continue
            for pos, node in enumerate(nodes[floor]):
                rooms_data.append({
                    'floor': floor,
                    'position': pos,
                    'node': node,
                    'floor_size': len(nodes[floor])
                })
        
        # Step 3: Calculate room counts for non-fixed floors only
        room_counts = self._calculate_room_counts(total_floors, nodes)
        
        # Step 4: Assign remaining rooms with constraints
        self._assign_remaining_rooms(rooms_data, room_counts, nodes)
    
    def _calculate_room_counts(self, total_floors: int, nodes: List[List[MapNode]]) -> Dict[RoomType, int]:
        """
        Calculate how many rooms of each type to generate based on probabilities.
        
        Based on ROOM_TYPE_WEIGHTS, calculates expected counts and rounds to integers.
        """
        # Count total nodes (excluding fixed floors that will be assigned separately)
        # Fixed floors: 0 (NEO), 1 (M), 9 (T), 15 (R), 16 (B), 17 (T)
        fixed_floor_indices = {0, 1, 9, 15, 16, 17}
        
        total_nodes = 0
        for floor in range(total_floors):
            if floor not in fixed_floor_indices:
                total_nodes += len(nodes[floor])
        
        # Calculate from room weights
        # The weights represent distribution across all non-fixed rooms
        total_weight = sum(self.ROOM_TYPE_WEIGHTS.values())
        
        # Calculate counts
        counts = {}
        for room_type, weight in self.ROOM_TYPE_WEIGHTS.items():
            # Calculate expected count based on weight proportion
            if room_type == RoomType.UNKNOWN:
                # Unknown rooms resolve to other types, so skip in count calculation
                continue
            counts[room_type] = int(weight * total_nodes / total_weight)
        
        # Fill remaining with MONSTER
        assigned_count = sum(counts.values())
        counts[RoomType.MONSTER] += (total_nodes - assigned_count)
        
        # Ensure all room types in available list are in counts
        # Add EVENT type with 0 count if not present
        if RoomType.EVENT not in counts:
            counts[RoomType.EVENT] = 0
        
        return counts
    
    def _assign_fixed_floors(self, rooms_data: List[Dict], room_counts: Dict[RoomType, int], nodes: List[List[MapNode]]):
        """
        Assign room types to fixed floors.
        
        Fixed assignments:
        - Floor 0: NEO
        - Floor 1: MONSTER
        - Floor 9: TREASURE
        - Floor 15: REST
        - Floor 16: BOSS
        - Floor 17: TREASURE
        """
        for room_info in rooms_data:
            floor = room_info['floor']
            node = room_info['node']
            
            if floor == 0:
                node.room_type = RoomType.NEO
                room_info['assigned'] = True
            elif floor == 1:
                node.room_type = RoomType.MONSTER
                room_info['assigned'] = True
            elif floor == 9:
                node.room_type = RoomType.TREASURE
                room_info['assigned'] = True
            elif floor == 15:
                node.room_type = RoomType.REST
                room_info['assigned'] = True
            elif floor == 16:
                node.room_type = RoomType.BOSS
                room_info['assigned'] = True
            elif floor == 17:
                node.room_type = RoomType.TREASURE
                room_info['assigned'] = True
            else:
                room_info['assigned'] = False
    
    def _assign_remaining_rooms(self, rooms_data: List[Dict], room_counts: Dict[RoomType, int], nodes: List[List[MapNode]]):
        """
        Assign room types to non-fixed floor nodes respecting all constraints.
        
        Note: This method only receives rooms_data for non-fixed floors.
        Fixed floors are already assigned in _assign_normal_act_rooms and are not passed here.
        
        Constraints:
        1. No elite/rest in first 5 floors (floors 2-4, since 0-1 are fixed)
        2. No rest on floor 14
        3. No consecutive elite/rest/shop rooms between adjacent floors
        4. Floor 8 rooms have diverse types (for floor 9 treasure)
        5. No duplicate room types within same floor
        """
        # All rooms in rooms_data are unassigned (fixed floors are already excluded)
        unassigned = rooms_data
        
        # Sort by floor to ensure lower floors get assigned first
        unassigned.sort(key=lambda x: x['floor'])
        
        # Track previous room type for consecutive check
        prev_room_types = {}  # floor -> room_type
        
        # Track assigned room types within each floor
        assigned_this_floor = {}  # floor -> {position: room_type}
        
        for room_info in unassigned:
            floor = room_info['floor']
            position = room_info['position']
            node = room_info['node']
            
            # Get assigned types for this floor (excluding current position)
            floor_assigned = {
                pos: rtype 
                for pos, rtype in assigned_this_floor.get(floor, {}).items() 
                if pos != position
            }
            
            # Get available room types for this floor position
            available_types = self._get_available_types_for_floor(
                floor, 
                position, 
                nodes, 
                prev_room_types,
                assigned_this_floor
            )
            
            # Choose a type from available types based on remaining counts
            chosen_type = self._choose_type_from_available(available_types, room_counts)
            
            # Assign and update counts
            node.room_type = chosen_type
            room_counts[chosen_type] -= 1
            prev_room_types[floor] = chosen_type
            
            # Track this assignment for the floor
            if floor not in assigned_this_floor:
                assigned_this_floor[floor] = {}
            assigned_this_floor[floor][position] = chosen_type
    
    def _get_available_types_for_floor(
        self, 
        floor: int, 
        position: int, 
        nodes: List[List[MapNode]],
        prev_room_types: Dict[int, RoomType],
        assigned_this_floor: Dict[int, RoomType]
    ) -> List[RoomType]:
        """
        Get list of available room types for a specific floor position.
        
        Constraints:
        - No elite/rest in first 5 floors (floors 2-4, since 0-1 are fixed)
        - No rest on floor 14
        - No consecutive elite/rest/shop between adjacent floors
        - Floor 8: ensure diversity from previous floor's outgoing rooms
        - All rooms on floor 8 connect to different room types (for floor 9 treasure)
        - No duplicate room types within the same floor's connections
        
        Args:
            floor: Current floor being assigned
            position: Position index on current floor
            nodes: All nodes in the map
            prev_room_types: Room types already assigned to previous floors
            assigned_this_floor: Room types already assigned to positions on this floor
            
        Returns:
            List of available RoomType for this position
        """
        available = [RoomType.MONSTER, RoomType.ELITE, RoomType.REST, 
                   RoomType.MERCHANT, RoomType.EVENT]
        
        # Constraint 1: No elite/rest in first 5 floors (floors 2-4)
        if floor <= 4:
            available = [t for t in available if t not in [RoomType.ELITE, RoomType.REST]]
        
        # Constraint 2: No rest on floor 14
        if floor == 14:
            available = [t for t in available if t != RoomType.REST]
        
        # Constraint 3: No consecutive elite/rest/shop between adjacent floors
        # Check if previous floor has any REST/ELITE/MERCHANT rooms
        if floor > 0:
            prev_floor_types = set()
            for node in nodes[floor - 1]:
                prev_floor_types.add(node.room_type)
            
            # If previous floor has REST/ELITE/MERCHANT, avoid those types
            if prev_floor_types & {RoomType.ELITE, RoomType.REST, RoomType.MERCHANT}:
                available = [t for t in available if t not in prev_floor_types]
        
        # Constraint 4: Floor 8 must have diverse types (for floor 9 treasure)
        # All rooms on floor 8 should connect to different room types on floor 9
        if floor == 8:
            # Get room types already assigned on floor 8
            floor8_types = set()
            if assigned_this_floor and floor in assigned_this_floor:
                floor8_types = set(assigned_this_floor[floor].values())
            # For floor 8, avoid types already used on this floor
            available = [t for t in available if t not in floor8_types]
        
        # Constraint 5: Avoid duplicate room types within the same floor
        # Don't assign the same type as already assigned on this floor
        if assigned_this_floor and floor in assigned_this_floor:
            used_types = set(assigned_this_floor[floor].values())
            available = [t for t in available if t not in used_types]
        
        return available
    
    def _choose_type_from_available(
        self, 
        available_types: List[RoomType], 
        room_counts: Dict[RoomType, int]
    ) -> RoomType:
        """
        Choose a room type from available types, preferring those with remaining counts.
        
        Args:
            available_types: List of valid room types for this position
            room_counts: Remaining count of each room type to assign
            
        Returns:
            Chosen RoomType
        """
        # Filter to only types with remaining count > 0
        valid_types = [t for t in available_types if room_counts.get(t, 0) > 0]
        
        if valid_types:
            # Choose weighted by remaining count
            total_remaining = sum(room_counts[t] for t in valid_types)
            
            if total_remaining == 0:
                return self.rng.choice(valid_types)
            
            # Weighted random choice
            weights = [room_counts[t] / total_remaining for t in valid_types]
            return self.rng.choices(valid_types, weights=weights, k=1)[0]
        
        # Fallback: if no valid types due to constraints, try relaxed constraints
        # Return the first available type regardless of count
        # This allows the map to complete even if exact counts can't be met
        return self.rng.choice(available_types) if available_types else RoomType.MONSTER
    
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
            Room instance for target node
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
        Display the map in a human-friendly format.
        
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
        tui_print(t("ui.map_view", act=act_num, floor=current_floor))
        tui_print("="*60)
        
        act_start_floor = self._get_act_start_floor(self.act_id)
        debug_config = game_state.config.debug
        if isinstance(debug_config, dict):
            debug_enabled = bool(debug_config.get("print", False))
        else:
            debug_enabled = bool(debug_config)
        if debug_enabled:
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
        tui_print(f"\n{t('ui.legend')}")
        tui_print(f"  {t('ui.legend_monster')}  {t('ui.legend_elite')}  {t('ui.legend_merchant')}  {t('ui.legend_event')}")
        tui_print(f"  {t('ui.legend_rest')}  {t('ui.legend_treasure')}  {t('ui.legend_boss')}  {t('ui.legend_neo')}")
        tui_print(f"  {t('ui.legend_current')}   {t('ui.legend_available')}   {t('ui.legend_visited')}")
        tui_print(f"  {t('ui.map_connection_help', default='Indices are above nodes. Lines show exact connections to the next floor.')}")
        tui_print()
        
        # Calculate true floor starting point for this act
        act_start_floor = self._get_act_start_floor(self.act_id)
        
        # Display map floor by floor
        for floor in range(len(self.map_data.nodes)):
            floor_nodes = self.map_data.nodes[floor]
            if not floor_nodes:
                continue
            
            next_floor_nodes = self.map_data.nodes[floor + 1] if floor + 1 < len(self.map_data.nodes) else None

            true_floor = act_start_floor + floor
            label = f"{t('ui.floor_label', num=true_floor)} "
            for line in self._render_floor_block(
                label=label,
                floor=floor,
                true_floor=true_floor,
                floor_nodes=floor_nodes,
                next_floor_nodes=next_floor_nodes,
                current_floor_act=self.map_data.current_floor,
                current_position=current_position,
                available_positions=available_positions,
                visited_positions=visited_positions,
            ):
                tui_print(line)
        
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
            # Localize room type
            room_type_localized = t(f'ui.room_type.{node.room_type.name.upper()}', default=node.room_type.value)
            available_moves_data.append({
                "index": idx,
                "floor": true_floor,
                "position": node.position,
                "room_type": room_type_localized,
                "risk_level": self._get_risk_level(node.room_type),
                "reward_level": self._get_reward_level(node.room_type)
            })
        
        # Generate map structure JSON
        map_structure = []
        for floor in range(len(self.map_data.nodes)):
            floor_data = []
            for pos, node in enumerate(self.map_data.nodes[floor]):
                # Localize room type
                room_type_localized = t(f'ui.room_type.{node.room_type.name.upper()}', default=node.room_type.value)
                floor_data.append({
                    "position": pos,
                    "room_type": room_type_localized,
                    "visited": (floor, pos) in visited_positions,
                    "connections_up": node.connections_up
                })
        
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

            true_floor = act_start_floor + floor
            label = f"Floor {true_floor:2d}: "
            next_floor_nodes = self.map_data.nodes[floor + 1] if floor < len(self.map_data.nodes) - 1 else None
            lines.extend(
                self._render_floor_block(
                    label=label,
                    floor=floor,
                    true_floor=true_floor,
                    floor_nodes=floor_nodes,
                    next_floor_nodes=next_floor_nodes,
                    current_floor_act=current_floor_act,
                    current_position=current_position,
                    available_positions=available_positions,
                    visited_positions=visited_positions,
                )
            )
        
        return "\n".join(lines)

    def _format_floor_nodes_line(
        self,
        label: str,
        floor: int,
        true_floor: int,
        floor_nodes: List[MapNode],
        current_floor_act: int,
        current_position: int,
        available_positions: set,
        visited_positions: set,
    ) -> str:
        """Format a floor line using fixed grid slots for each node."""
        row = self._blank_map_row()
        slots = self._slot_columns_for_count(len(floor_nodes))
        for pos, (node, slot) in enumerate(zip(floor_nodes, slots)):
            symbol = self._get_room_symbol(node.room_type)
            prefix = " "

            if floor == current_floor_act and pos == current_position:
                prefix = "*"
            elif (true_floor, pos) in available_positions:
                prefix = ">"
            elif (true_floor, pos) in visited_positions:
                prefix = "^"

            node_text = f"[{prefix}{symbol}]"
            start = slot * self.MAP_SLOT_WIDTH
            row[start:start + len(node_text)] = list(node_text)

        return label + "".join(row).rstrip()

    def _slot_columns_for_count(self, count: int) -> List[int]:
        """Return fixed slot columns for a floor node count."""
        if count not in self.MAP_SLOT_LAYOUTS:
            raise ValueError(f"Unsupported floor node count: {count}")
        return list(self.MAP_SLOT_LAYOUTS[count])

    def _slot_center(self, slot: int) -> int:
        """Return the center column for a slot index."""
        return slot * self.MAP_SLOT_WIDTH + 2

    def _blank_map_row(self) -> List[str]:
        """Create an empty row for the fixed-width map canvas."""
        return list(" " * (self.MAP_SLOT_WIDTH * 5))

    def _format_floor_index_line(self, label: str, floor_nodes: List[MapNode]) -> str:
        """Render visible position indices above the node row."""
        row = self._blank_map_row()
        for pos, slot in enumerate(self._slot_columns_for_count(len(floor_nodes))):
            row[slot * self.MAP_SLOT_WIDTH] = str(pos)
        return label + "".join(row).rstrip()

    def _draw_connection_rows(self, floor_nodes: List[MapNode], next_floor_nodes: List[MapNode]) -> List[str]:
        """Draw five rows of ASCII connections between adjacent floors."""
        row_depart = self._blank_map_row()
        row_turn = self._blank_map_row()
        row_cruise = self._blank_map_row()
        row_approach = self._blank_map_row()
        row_land = self._blank_map_row()
        src_slots = self._slot_columns_for_count(len(floor_nodes))
        dst_slots = self._slot_columns_for_count(len(next_floor_nodes))

        def mark(buffer: List[str], index: int, char: str) -> None:
            if not (0 <= index < len(buffer)):
                return
            current = buffer[index]
            if current == " ":
                buffer[index] = char
            elif current == char:
                return
            elif current in "-|" and char in "-|":
                buffer[index] = "+"
            elif current in "/\\" and char in "/\\" and current != char:
                buffer[index] = "X"
            elif current in "/\\" and char in "-|":
                buffer[index] = "+"
            elif current in "-|" and char in "/\\":
                buffer[index] = "+"

        for src_pos, src_node in enumerate(floor_nodes):
            src_center = self._slot_center(src_slots[src_pos])
            for dest_pos in sorted(src_node.connections_up):
                if not (0 <= dest_pos < len(next_floor_nodes)):
                    continue
                dest_center = self._slot_center(dst_slots[dest_pos])
                if dest_center == src_center:
                    mark(row_depart, src_center, "|")
                    mark(row_turn, src_center, "|")
                    mark(row_cruise, src_center, "|")
                    mark(row_approach, src_center, "|")
                    mark(row_land, src_center, "|")
                    continue

                direction = 1 if dest_center > src_center else -1
                first_step = src_center + direction
                pre_dest = dest_center - direction
                mark(row_depart, src_center, "|")
                mark(row_turn, first_step, "\\" if direction > 0 else "/")

                horizontal_start = min(first_step, pre_dest)
                horizontal_end = max(first_step, pre_dest)
                for idx in range(horizontal_start + 1, horizontal_end):
                    mark(row_cruise, idx, "-")
                mark(row_approach, pre_dest, "\\" if direction > 0 else "/")
                mark(row_land, dest_center, "|")

        rendered = [
            "".join(row_depart).rstrip(),
            "".join(row_turn).rstrip(),
            "".join(row_cruise).rstrip(),
            "".join(row_approach).rstrip(),
            "".join(row_land).rstrip(),
        ]
        return [row for row in rendered if row.strip()]

    def _render_floor_block(
        self,
        label: str,
        floor: int,
        true_floor: int,
        floor_nodes: List[MapNode],
        next_floor_nodes: Optional[List[MapNode]],
        current_floor_act: int,
        current_position: int,
        available_positions: set,
        visited_positions: set,
    ) -> List[str]:
        """Render one floor as index row, node row, and optional connection rows."""
        lines = [
            self._format_floor_index_line(" " * len(label), floor_nodes),
            self._format_floor_nodes_line(
                label=label,
                floor=floor,
                true_floor=true_floor,
                floor_nodes=floor_nodes,
                current_floor_act=current_floor_act,
                current_position=current_position,
                available_positions=available_positions,
                visited_positions=visited_positions,
            ),
        ]
        if next_floor_nodes:
            for conn_row in self._draw_connection_rows(floor_nodes, next_floor_nodes):
                lines.append(" " * len(label) + conn_row)
        return lines

    def get_map_text_for_human(self) -> str:
        """
        Get map text block for TUI display panel (no printing).
        
        Design principles (same as display_map_for_human):
        - Fixed node width: [?M] (4 chars) for consistent alignment
        - Each node shows outgoing connections below: / (left), | (center), \\ (right)
        - Max 3 outgoing and 3 incoming connections per node
        """
        from engine.game_state import game_state

        current_floor = game_state.current_floor
        act_num = game_state.current_act
        available_moves = self.get_available_moves()
        available_positions = {(node.floor, node.position) for node in available_moves}

        # Get current position
        current_position = self.map_data.current_position

        # Get visited nodes (historical path taken)
        act_start_floor = self._get_act_start_floor(self.act_id)
        visited_positions = {
            (act_start_floor + floor_in_act, pos)
            for floor_in_act, pos in self.map_data.visited_path
        }

        lines = []
        lines.append("=" * 60)
        lines.append(t("ui.map_view", default="MAP VIEW - Act {act} (Floor {floor})", act=act_num, floor=current_floor))
        lines.append("=" * 60)
        
        # Legend
        lines.append("")
        lines.append(t("ui.legend", default="Legend:"))
        lines.append(f"  {t('ui.legend_monster')}  {t('ui.legend_elite')}  {t('ui.legend_merchant')}  {t('ui.legend_event')}")
        lines.append(f"  {t('ui.legend_rest')}  {t('ui.legend_treasure')}  {t('ui.legend_boss')}  {t('ui.legend_neo')}")
        lines.append(f"  {t('ui.legend_current')}   {t('ui.legend_available')}   {t('ui.legend_visited')}")
        lines.append(f"  {t('ui.map_connection_help', default='Indices are above nodes. Lines show exact connections to the next floor.')}")
        lines.append("")

        # Display map floor by floor
        for floor in range(len(self.map_data.nodes)):
            floor_nodes = self.map_data.nodes[floor]
            if not floor_nodes:
                continue

            next_floor_nodes = self.map_data.nodes[floor + 1] if floor + 1 < len(self.map_data.nodes) else None

            true_floor = act_start_floor + floor
            label = f"{t('ui.floor_label', default='Floor {num}:', num=true_floor)} "
            lines.extend(
                self._render_floor_block(
                    label=label,
                    floor=floor,
                    true_floor=true_floor,
                    floor_nodes=floor_nodes,
                    next_floor_nodes=next_floor_nodes,
                    current_floor_act=self.map_data.current_floor,
                    current_position=current_position,
                    available_positions=available_positions,
                    visited_positions=visited_positions,
                )
            )

        lines.append("")
        lines.append("=" * 60)
        
        # Escape square brackets for Rich/Textual markup
        # Rich treats [...] as markup tags, so we need to escape them
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
