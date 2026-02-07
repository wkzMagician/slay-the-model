"""
Global game state management for persistent data

Global action queue architecture:
- All rooms, events, and combat share the same global action_queue
- Use game_state.execute_all_actions() to execute queued actions
- No individual action queues in rooms/events/combat
"""
import random as rd
from typing import Optional
from utils.result_types import BaseResult
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

        # Gold spending tracking for MawBank relic
        self.gold_spent_in_shop = 0

        # Current room and event tracking
        self.current_room: Optional[Room] = None
        self.event_stack = []
        
        # Global action queue - shared across all rooms and events
        from actions.base import ActionQueue
        self.action_queue = ActionQueue()
        
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

    def execute_all_actions(self) -> BaseResult:
        """
        Execute all actions in the global action queue.

        This is the central action execution method that all rooms
        and events should use instead of managing their own queues.

        Supports both new BaseResult types and legacy return patterns
        for backward compatibility.

        Returns:
            BaseResult if special result encountered, NoneResult otherwise
        """
        from utils.result_types import (
            BaseResult, SingleActionResult, MultipleActionsResult,
            GameStateResult, NoneResult
        )
        from actions.base import Action
        from actions.display import SelectAction

        result = None
        while not self.action_queue.is_empty():
            result = self.action_queue.execute_next()

            # Check if action returned something to process
            if result is not None:
                # Handle legacy returns (Action, List[Action], str) directly
                # for backward compatibility with actions that haven't been updated
                from actions.base import Action

                assert result is BaseResult
                
                # BaseResult types - handle appropriately
                if isinstance(result, SingleActionResult):
                    self.action_queue.add_action(result.action, to_front=True)
                elif isinstance(result, MultipleActionsResult):
                    self.action_queue.add_actions(result.actions, to_front=True)
                elif isinstance(result, GameStateResult):
                    return result
                # NoneResult: nothing to queue, continue loop
                elif isinstance(result, NoneResult):
                    pass

        return NoneResult()

    @property
    def current_event(self):
        """Get current event (top of stack)"""
        return self.event_stack[-1] if self.event_stack else None


# Global game state instance
game_state = GameState()