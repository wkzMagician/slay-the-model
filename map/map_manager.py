"""
Map manager for generating and navigating game maps.
"""
from typing import List, Dict, TYPE_CHECKING, Optional
from localization import t
from utils.types import RoomType
from .map_node import MapNode
from .map_data import MapData
from .encounter_pool import EncounterPool
from engine.random_streams import RandomStreams, StreamRandom, using_streams

from tui.print_utils import tui_print
# Avoid circular import - use TYPE_CHECKING for type hints
if TYPE_CHECKING:
    from rooms.base import Room


class MapManager:
    """
    Manages map generation and navigation for a single act.
    
    Normal acts adapt a 15-by-7 original path grid to compact selectable
    positions, with separate entry, boss and exit rows. Act 4 is a fixed chain.
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
        6: [0, 1, 2, 4, 5, 6],
        7: list(range(7)),
        1: [2],
        2: [1, 3],
        3: [0, 2, 4],
        4: [0, 1, 3, 4],
        5: [0, 1, 2, 3, 4],
    }
    MAP_SLOT_WIDTH = 8
    
    def __init__(self, seed: int, act_id: int = 1, deadly_events: bool = False,
                 random_streams: RandomStreams | None = None):
        """
        Initialize map manager.
        
        Args:
            seed: Random seed for deterministic generation
            act_id: The act number (default: 1)
            deadly_events: Whether Deadly Events modifier is active (default: False)
        """
        self.seed = seed
        self.act_id = act_id
        self.random_streams = random_streams if random_streams is not None else RandomStreams(seed)
        self.rng = self.random_streams.map_rng if random_streams is not None else StreamRandom(seed)
        self.map_data = MapData(act_id)
        self.deadly_events = deadly_events
        
        # Initialize encounter pool system
        self.encounter_pool = EncounterPool(seed, act_id=act_id, streams=self.random_streams)
        
        # Track visits to each ? room type for "bad luck protection"
        # Each increment represents a visit that didn't result in that type
        self.unknown_room_visits = {
            RoomType.MONSTER: 0,    # Starts at 10%, +10% per non-monster visit
            RoomType.MERCHANT: 0,    # Starts at 3%, +3% per non-merchant visit
            RoomType.TREASURE: 0,     # Starts at 2%, +2% (or +4%) per non-treasure visit
            RoomType.ELITE: 0,        # Starts at 20% (only with deadly_events, floor 6+), +20% per non-elite visit
        }
        
        self.relic_effects = {}
        
        # Relic effects that modify unknown room probabilities
        self._relic_effects = {
            'juzu_bracelet': False,
        }
        
        # Store floor counts per act for accurate true floor calculation
        # This is populated when maps are generated for each act
        self._act_floor_counts = {}
        self.original_grid = None
        self.generated_room_counts = {}
    
    def set_relic_effect(self, effect_name: str, enabled: bool) -> None:
        """
        Enable or disable a relic effect that modifies unknown room probabilities.
        
        Args:
            effect_name: Name of relic effect (e.g., 'juzu_bracelet')
            enabled: Whether the effect is active
        """
        if effect_name in self._relic_effects:
            self._relic_effects[effect_name] = enabled
    
    def generate_map(self) -> MapData:
        """Generate original normal-mode grid, then adapt navigation coordinates."""
        from engine.game_state import game_state
        from .original_map import generate_paths, assign_rooms

        act_start = self._get_act_start_floor(self.act_id)
        if self.act_id == 4:
            kinds = [RoomType.REST, RoomType.MERCHANT, RoomType.ELITE,
                     RoomType.BOSS, RoomType.VICTORY]
            nodes = [[MapNode(act_start + row, 0, kind, [0] if row < 4 else [])]
                     for row, kind in enumerate(kinds)]
        else:
            self.original_grid = generate_paths(self.rng)
            self.generated_room_counts = assign_rooms(self.original_grid, self.rng, game_state.ascension)
            connected = [[node for node in row if node.edges] for row in self.original_grid]
            positions = [{node.x: index for index, node in enumerate(row)} for row in connected]
            entry = MapNode(act_start, 0, RoomType.NEO, list(range(len(connected[0]))))
            entry.map_x = 3
            nodes = [[entry]]
            for y, row in enumerate(connected):
                compact = []
                for position, original in enumerate(row):
                    destinations = ([positions[y + 1][x] for x in original.edges]
                                    if y < 14 else [0])
                    node = MapNode(act_start + y + 1, position,
                                   original.room_type or RoomType.MONSTER, destinations)
                    node.map_x = original.x
                    compact.append(node)
                nodes.append(compact)
            tail = ([RoomType.BOSS, RoomType.BOSS, RoomType.VICTORY]
                    if self.act_id == 3 and game_state.ascension >= 20 else
                    [RoomType.BOSS, RoomType.VICTORY if self.act_id == 3 else RoomType.TREASURE])
            for offset, kind in enumerate(tail):
                node = MapNode(act_start + 16 + offset, 0, kind,
                               [0] if offset < len(tail) - 1 else [])
                node.map_x = 3
                nodes.append([node])
        self._act_floor_counts[self.act_id] = len(nodes)
        self.map_data.nodes = nodes
        return self.map_data

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
        return self._player_has_relic("tiny_chest") or self._player_has_relic("tinychest")

    @property
    def has_juzu_bracelet(self) -> bool:
        return self._player_has_relic("juzu_bracelet") or self._player_has_relic("juzubracelet") or self._relic_effects.get("juzu_bracelet", False)

    @property
    def has_ssserpent_head(self) -> bool:
        return self._player_has_relic("ssserpent_head") or self._player_has_relic("ssserpenthead")
    
    def _wing_boots(self):
        return next((relic for relic in self._get_player_relics()
                     if getattr(relic, "idstr", None) == "WingBoots"
                     and getattr(relic, "charges", 0) > 0), None)

    def _can_move_to(self, node: MapNode) -> bool:
        current = self.map_data.get_current_node()
        return (
            current is not None
            and node.floor == self._get_act_start_floor(self.act_id) + self.map_data.current_floor + 1
            and (node.position in current.connections_up
                 or (bool(current.connections_up) and self._wing_boots() is not None))
        )

    def get_available_moves(self) -> List[MapNode]:
        """
        Get all nodes that can be moved to from the current position.
        
        Returns:
            List of MapNode objects that are reachable from current position
        """
        if self.map_data.current_floor >= len(self.map_data.nodes) - 1:
            return []
        
        next_floor = self.map_data.current_floor + 1
        current = self.map_data.get_current_node()
        if current is None:
            return []
        available = []
        for position in current.connections_up:
            node = self.map_data.get_node(next_floor, position)
            if node is not None and self._can_move_to(node):
                available.append(node)
        if self._wing_boots() is not None:
            available.extend(node for node in self.map_data.nodes[next_floor]
                             if node.position not in current.connections_up and self._can_move_to(node))
        return available
    
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
        if node is None or not self._can_move_to(node):
            raise ValueError("Destination must be an available node on the next floor")
        current = self.map_data.get_current_node()
        boots = self._wing_boots() if current is not None and position not in current.connections_up else None

        # Validate first, then establish this room's streams before constructing
        # enemies, random variants, or question-room contents.
        self.random_streams.enter_room(floor)
        from engine.game_state import game_state
        if getattr(game_state, "map_manager", None) is self:
            game_state.current_floor = floor
        
        # Create room instance based on room type
        with using_streams(self.random_streams):
            room = self._create_room_instance(node.room_type, floor_in_act=floor_in_act)
        
        # Update current position
        self.map_data.set_current_position(floor_in_act, position)
        if boots is not None:
            boots.charges -= 1
        
        return room
    
    def _create_room_instance(self, room_type: RoomType, floor_in_act: int | None = None):
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
        
        target_floor = self.map_data.current_floor if floor_in_act is None else floor_in_act

        if room_type == RoomType.MONSTER:
            # Get monster encounter from encounter pool
            enemies, encounter_name = self.encounter_pool.get_normal_encounter(
                floor=target_floor,
                encounter_count=game_state.normal_encounters_fought,
                encounter_history=game_state.encounter_history,
            )
            return CombatRoom(enemies=enemies, encounter_name=encounter_name)
        
        elif room_type == RoomType.ELITE:
            # Get elite encounter from encounter pool
            enemies, encounter_name = self.encounter_pool.get_elite_encounter(
                floor=target_floor,
                last_elite=game_state.elite_history[-1] if game_state.elite_history else None
            )
            return CombatRoom(enemies=enemies, room_type=RoomType.ELITE, encounter_name=encounter_name)
        
        elif room_type == RoomType.BOSS:
            # Boss combat room - fight the boss!
            boss_index = 0
            if self.act_id == 3 and game_state.ascension >= 20:
                boss_index = 0 if target_floor == 16 else 1
            enemies, encounter_name = self.encounter_pool.get_boss_encounter(
                floor=target_floor,
                boss_index=boss_index,
            )
            return CombatRoom(enemies=enemies, room_type=RoomType.BOSS, encounter_name=encounter_name)
        
        elif room_type == RoomType.REST:
            return RestRoom()
        
        elif room_type == RoomType.MERCHANT:
            return ShopRoom()
        
        elif room_type == RoomType.TREASURE:
            is_boss = target_floor == 17 and self.act_id < 3
            return TreasureRoom(is_boss=is_boss)
        
        elif room_type == RoomType.EVENT:
            return EventRoom()
        
        elif room_type == RoomType.VICTORY:
            return VictoryRoom()
        
        elif room_type == RoomType.UNKNOWN:
            # Resolve unknown room type
            actual_type = self._resolve_unknown_type(target_floor)
            return self._create_room_instance(actual_type, floor_in_act=target_floor)
        
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
        slots = self._slots_for_nodes(floor_nodes)
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

    def _slots_for_nodes(self, nodes: List[MapNode]) -> List[int]:
        if all(node.map_x is not None for node in nodes):
            return [int(node.map_x) for node in nodes if node.map_x is not None]
        return self._slot_columns_for_count(len(nodes))

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
        return list(" " * (self.MAP_SLOT_WIDTH * 7))

    def _format_floor_index_line(self, label: str, floor_nodes: List[MapNode]) -> str:
        """Render visible position indices above the node row."""
        row = self._blank_map_row()
        for pos, slot in enumerate(self._slots_for_nodes(floor_nodes)):
            row[slot * self.MAP_SLOT_WIDTH] = str(pos)
        return label + "".join(row).rstrip()

    def _draw_connection_rows(self, floor_nodes: List[MapNode], next_floor_nodes: List[MapNode]) -> List[str]:
        """Draw five rows of ASCII connections between adjacent floors."""
        row_depart = self._blank_map_row()
        row_turn = self._blank_map_row()
        row_cruise = self._blank_map_row()
        row_approach = self._blank_map_row()
        row_land = self._blank_map_row()
        src_slots = self._slots_for_nodes(floor_nodes)
        dst_slots = self._slots_for_nodes(next_floor_nodes)

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
        from relics.global_relics.common import TinyChest

        tiny_chest = next(
            (relic for relic in self._get_player_relics() if isinstance(relic, TinyChest)),
            None,
        )
        if tiny_chest is not None and tiny_chest.advance_unknown_room():
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
        
        # Event fills remaining probability
        total_chances = monster_chance + treasure_chance + shop_chance + elite_chance
        event_chance = 100 - total_chances
        
        # Roll for encounter type
        roll = self.random_streams["event"].randint(1, 100)
        
        rolled_monster = roll <= monster_chance
        if rolled_monster:
            chosen_type = RoomType.MONSTER
        elif roll <= monster_chance + treasure_chance:
            chosen_type = RoomType.TREASURE
        elif roll <= monster_chance + treasure_chance + shop_chance:
            chosen_type = RoomType.MERCHANT
        elif roll <= monster_chance + treasure_chance + shop_chance + elite_chance:
            chosen_type = RoomType.ELITE
        else:
            chosen_type = RoomType.EVENT  # Event

        if rolled_monster and self.has_juzu_bracelet:
            chosen_type = RoomType.EVENT
        
        redirected_from_monster = rolled_monster and chosen_type == RoomType.EVENT

        # Reset visit counter for the chosen type
        if rolled_monster:
            self.unknown_room_visits[RoomType.MONSTER] = 0
        else:
            self.unknown_room_visits[chosen_type] = 0
        
        # Increment visit counters for all other types
        for room_type in self.unknown_room_visits:
            if redirected_from_monster and room_type == RoomType.MONSTER:
                continue
            if room_type != chosen_type:
                self.unknown_room_visits[room_type] += 1
        
        # Ssserpent Head effect: gain 50 Gold
        if self.has_ssserpent_head:
            from engine.game_state import game_state
            game_state.player.gold += 50
            tui_print(t("ui.ssserpent_head_gold", default="Ssserpent Head: Gained 50 gold!"))
        
        return chosen_type
