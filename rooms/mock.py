"""
Mock room implementation - simulates a complete game run from floor 0 to floor 16.
This is used for automated testing and AI-mode game simulation.
"""
from engine.game_state import game_state
from rooms.base import Room
from utils.types import RoomType
from localization import t, LocalStr


class MockRoom(Room):
    """
    Mock room that simulates a complete game run through all 16 floors.
    
    This room automates the game flow by:
    1. Iterating through floors 0-16
    2. Making AI-mode decisions for map navigation
    3. Executing each room's init() and enter() methods
    4. Tracking WIN/DEATH conditions
    5. Displaying progress messages
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.room_type = None
        self.max_floor = 16  # Maximum floor number (0-16)
        self.use_ai_strategy = "least_risk"  # AI strategy: first, least_risk, highest_reward
        self.debug = True  # Display progress messages
    
    def init(self):
        """Initialize mock room - ensure map is ready"""
        # Map should already be initialized via game_state.initialize_map()
        pass
    
    def enter(self) -> str:
        """
        Enter and simulate complete game run through all floors.
        
        This method automates the game flow by iterating through all floors
        and making AI-mode decisions for room navigation.
        
        Returns:
            "WIN" if player reaches floor 16 with HP > 0
            "DEATH" if player HP drops to 0 or below during the run
        """
        self._display_progress("Starting automated game simulation...")
        self._display_progress(f"Target: Reach floor {self.max_floor}")
        
        # Main game loop - iterate through floors
        while game_state.current_floor < self.max_floor:
            # Check if player is still alive
            if game_state.player.current_hp <= 0:
                self._display_progress("\n💀 PLAYER DIED - SIMULATION FAILED 💀")
                self._display_progress(f"Final floor: {game_state.current_floor}")
                return "DEATH"
            
            # Get available moves from current position
            available_nodes = game_state.map_manager.get_available_moves()
            
            if not available_nodes:
                self._display_progress("\n⚠️ No more moves available!")
                break
            
            # Make AI decision for next node
            selected_node = self._make_ai_decision(available_nodes)
            
            # Display room selection
            self._display_room_selection(selected_node)
            
            # Move to node and create room
            room = game_state.map_manager.move_to_node(
                selected_node.floor,
                selected_node.position
            )
            
            # Update game state
            game_state.current_room = room
            
            # Initialize room
            room.init()
            
            # Enter room and execute its logic
            result = room.enter()
            
            # Check for death condition
            if result == "DEATH":
                self._display_progress(f"\n💀 DIED at floor {game_state.current_floor} 💀")
                self._display_progress(f"Room type: {selected_node.room_type.value}")
                room.leave()
                return "DEATH"
            
            # Check for win condition (though usually handled by floor check)
            if result == "WIN":
                self._display_progress("\n🎉 ROOM RETURNED WIN - GAME WON! 🎉")
                room.leave()
                return "WIN"
            
            # Leave room (cleanup)
            room.leave()
            
            # Display progress
            self._display_progress(
                f"Completed floor {game_state.current_floor} | "
                f"HP: {game_state.player.current_hp}/{game_state.player.max_hp} | "
                f"Gold: {game_state.player.gold}"
            )
        
        # Check final win condition
        if game_state.current_floor >= self.max_floor:
            if game_state.player.current_hp > 0:
                self._display_progress("\n🎉 WIN - REACHED FLOOR 16! 🎉")
                self._display_progress(f"Final HP: {game_state.player.current_hp}/{game_state.player.max_hp}")
                self._display_progress(f"Final Gold: {game_state.player.gold}")
                return "WIN"
            else:
                self._display_progress("\n💀 PLAYER DIED AT FINAL FLOOR 💀")
                return "DEATH"
        
        # Fallback - shouldn't reach here normally
        self._display_progress("\n⚠️ Simulation ended unexpectedly")
        return None
    
    def _make_ai_decision(self, available_nodes):
        """
        Make AI decision for selecting next room.
        
        Args:
            available_nodes: List of available MapNode objects
            
        Returns:
            Selected MapNode
        """
        if self.use_ai_strategy == "first":
            # Always select first available node
            return available_nodes[0]
        
        elif self.use_ai_strategy == "least_risk":
            # Select node with lowest risk level
            risk_priority = {
                RoomType.REST: 1,
                RoomType.MERCHANT: 2,
                RoomType.TREASURE: 3,
                RoomType.MONSTER: 4,
                RoomType.ELITE: 5,
                RoomType.BOSS: 6,
                RoomType.UNKNOWN: 7,
            }
            return min(
                available_nodes,
                key=lambda n: risk_priority.get(n.room_type, 99)
            )
        
        elif self.use_ai_strategy == "highest_reward":
            # Select node with highest reward level
            reward_priority = {
                RoomType.REST: 1,
                RoomType.MERCHANT: 2,
                RoomType.TREASURE: 4,
                RoomType.MONSTER: 3,
                RoomType.ELITE: 5,
                RoomType.BOSS: 6,
                RoomType.UNKNOWN: 2,
            }
            return max(
                available_nodes,
                key=lambda n: reward_priority.get(n.room_type, 0)
            )
        
        else:
            # Default: first node
            return available_nodes[0]
    
    def _display_room_selection(self, node):
        """Display selected room information"""
        room_symbol = game_state.map_manager._get_room_symbol(node.room_type)
        risk_level = game_state.map_manager._get_risk_level(node.room_type)
        reward_level = game_state.map_manager._get_reward_level(node.room_type)
        
        self._display_progress(
            f"→ Moving to Floor {node.floor}, Position {node.position} | "
            f"[{room_symbol}] {node.room_type.value} | "
            f"Risk: {risk_level} | Reward: {reward_level}"
        )
    
    def _display_progress(self, message):
        """Display progress message if debug mode is enabled"""
        if self.debug:
            print(f"[MockRoom] {message}")
