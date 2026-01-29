"""
Global game state management for persistent data
"""
import random as rd
from config.game_config import GameConfig
import os
import time
from .combat_state import CombatState


class GameState:
    """Global game state containing all persistent game data"""

    def __init__(self):
        # Player data
        self.player = None

        # Map data
        self.map_data = []
        self.map_connections = {}
        self.current_position = [0, 0]

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
        self.current_room = None
        self.event_stack = []
        
        # Combat state
        self.combat_state = CombatState()
        
        self.setup()
        
    def setup(self):
        if self.config.seed == -1:
            self.config.seed = int(time.time())
        rd.seed(self.config.seed)

    def handle_creature_death(self, creature):
        """Handle creature death notifications."""
        if creature is self.player:
            self.combat_state.game_phase = "game_over"

    @property
    def current_event(self):
        """Get the current event (top of the stack)"""
        return self.event_stack[-1] if self.event_stack else None


# Global game state instance
game_state = GameState()