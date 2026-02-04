"""
Global game state management for persistent data
"""
import random as rd
from typing import Optional
from config.game_config import GameConfig
import os
import time

from rooms.base import Room
from .combat_state import CombatState
from player.player_factory import create_player

class GameState:
    """Global game state containing all persistent game data"""

    def __init__(self):
        # Game progress
        self.current_floor = 0

        # Configuration
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "game_config.yaml")
        self.config = GameConfig.load(config_path)
        
        from localization import set_language
        set_language(self.config.language)

        # Run history for Neo blessings
        self.run_history = {"reached_exordium_boss": False}

        # Neo blessing effects
        self.neow_blessing_active = False
        self.neow_blessing_combat_count = 0

        # Key tracking for treasure events
        self.sapphire_key_picked = False

        # Tiny Chest relic tracking
        self.event_room_counter = 0

        # Current room and event tracking
        self.current_room: Optional[Room] = None
        self.event_stack = []
        
        # Note: action_queue is no longer in game_state
        # Each room/event now has its own action_queue
        
        # Game phase
        self.game_phase: str = "room"  # "map", "room", "menu", "gameover"
        
        # Combat state
        self.combat_state = CombatState()
        
        # game setup
        if self.config.seed == -1:
            self.config.seed = int(time.time())
        rd.seed(self.config.seed)
        # character
        self.player = create_player(self.config.character)

    def handle_creature_death(self, creature):
        """Handle creature death notifications."""
        if creature is self.player:
            self.game_phase = "game_over"
    
    def initialize_map(self):
        """Initialize the map system and generate the first act."""
        from map import MapManager
        
        self.map_manager = MapManager(self.config.seed, act_id=1)
        self.map_data = self.map_manager.generate_map()
        
        # Set game phase to map
        self.game_phase = "map"

    @property
    def current_event(self):
        """Get the current event (top of the stack)"""
        return self.event_stack[-1] if self.event_stack else None


# Global game state instance
game_state = GameState()