"""
Global game state management for persistent data

Global action queue architecture:
- All rooms, events, and combat share the same global action_queue
- Use game_state.execute_all_actions() to execute queued actions
- No individual action queues in rooms/events/combat
"""
import random as rd
from typing import List, Optional

from engine.input_protocol import InputRequest, InputSubmission
from engine.message_bus import MessageBus
from engine.runtime_context import RuntimeContext
from utils.result_types import BaseResult, GameStateResult
from config.game_config import GameConfig
import os
import time

from rooms.base import Room
from .combat_state import CombatState
from .combat import Combat
from player.player_factory import create_player

# Constants for multi-act support
MAX_ACTS = 4

class GameState:
    """Global game state containing all persistent game data"""

    def __init__(self):
        # Multi-act game progress
        self.current_act: int = 1          # Current act (1-4)
        self.floor_in_act: int = 0         # Floor within current act (0-17)
        self.ascension: int = 0            # Ascension level (0-20, 0 = no ascension) - set after config load

        # Keys for Act 4 access (defeat act 3 boss with all 3 keys to enter act 4)
        self.ruby_key: bool = False        # From boss relic
        self.emerald_key: bool = False     # From chest
        self.sapphire_key: bool = False    # From specific events (already tracked)

        # Configuration
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "game_config.yaml")
        self.config = GameConfig.load(config_path)
        
        from localization import set_language
        set_language(self.config.language)
        
        # Ascension from config
        self.ascension = self.config.ascension

        # Run history for Neo blessings
        self.run_history = {"reached_exordium_boss": False}

        # Track obtained relics (global, even if removed later)
        self.obtained_relics: set = set()
        
        # Event stack for nested event contexts
        self.event_stack = []

        # Neo blessing effects
        self.neow_blessing_active = False
        self.neow_blessing_combat_count = 0

        # Key tracking for treasure events
        self.sapphire_key_picked = False

        # Tiny Chest relic tracking
        self.event_room_counter = 0

        # Gold spending tracking for MawBank relic
        self.gold_spent_in_shop = 0

        # Card chance rolling offset (each common card gained increases rare chance)
        self.card_chance_common_counter = 0

        # Potion drop chance (40% base, -10% after drop, +10% after no drop)
        self.potion_drop_chance = 40

        # Normal encounter counter for encounter pool selection
        # First 3 encounters use easy pool, rest use hard pool
        self.normal_encounters_fought = 0
        
        # Encounter history for constraint rules
        # Same encounter cannot appear in next 2 encounters
        self.encounter_history: List[str] = []
        
        # Elite history for elite constraint rules
        # Same elite cannot appear twice in a row
        self.elite_history: List[str] = []

        # Current room tracking
        self.current_room: Optional[Room] = None
        
        # Global action queue - shared across all rooms and events
        from actions.base import ActionQueue
        self.action_queue = ActionQueue()
        self.message_bus = MessageBus()
        
        # Current combat (None when not in combat)
        self.current_combat: Optional[Combat] = None
        # AI Decision Engine (initialized if in AI mode with valid config)
        self.decision_engine = None
        if self.config.mode == "ai" and self.config.ai.get("api_key"):
            from ai.ai_interface import LLMDecisionEngine
            self.decision_engine = LLMDecisionEngine(self.config.ai, debug=True)
        
        
        # game setup
        if self.config.seed == -1:
            self.config.seed = int(time.time())
        rd.seed(self.config.seed)
        # character
        self.player = create_player(self.config.character)
        
        # temp value for select result
        self.last_select_idx = -1
        self.runtime_context = RuntimeContext(game_state=self)

    def publish_message(self, message, participants: Optional[List] = None) -> List:
        """Publish a runtime message and return follow-up actions."""
        return self.message_bus.publish(message, participants=participants)

    def message_participants(self, enemies=None, include_hand: bool = False, hand=None) -> List:
        """Build the standard runtime participant list for message dispatch."""
        return self.runtime_context.message_participants(
            enemies=enemies,
            include_hand=include_hand,
            hand=hand,
        )
    
    def _get_floors_in_act(self, act: int) -> int:
        """
        Get actual floor count for specified act.
        
        Args:
            act: Act number (1-4)
            
        Returns:
            Number of floors in this act
        """
        if act == 4:
            return 6  # Act 4: 6 floors (0-5)
        elif act == 3 and self.ascension >= 20:
            return 19  # Act 3 A20+: 19 floors (0-18)
        else:
            return 18  # Default: 18 floors (0-17)
        
    def _get_max_floor_in_act(self, act: int) -> int:
        return self._get_floors_in_act(act) - 1
    
    def get_true_floor(self) -> int:
        """
        Get absolute floor number across all acts.
        
        Calculates the total floor count by summing all previous acts'
        floor counts plus the current floor within this act.
        
        Returns:
            Absolute floor number (0-indexed)
        """
        total = 0
        for act in range(1, self.current_act):
            total += self._get_max_floor_in_act(act)
        total += self.floor_in_act
        return total
    
    @property
    def current_floor(self) -> int:
        """Total floor count across all acts (for backward compatibility and display)."""
        return self.get_true_floor()

    @property
    def combat(self) -> Optional[Combat]:
        """Backward-compatible alias for current combat instance."""
        return self.current_combat

    @combat.setter
    def combat(self, value: Optional[Combat]):
        self.current_combat = value
    
    @current_floor.setter
    def current_floor(self, value: int):
        """Setter for backward compatibility - derives act and floor_in_act from total."""
        # Calculate which act this floor belongs to
        total = value
        self.current_act = 1
        
        # Subtract each act's floors until we find the right one
        while total >= self._get_max_floor_in_act(self.current_act):
            total -= self._get_max_floor_in_act(self.current_act)
            self.current_act += 1
        
        # Remaining floors is floor_in_act
        self.floor_in_act = total
    
    @property
    def has_all_keys(self) -> bool:
        """Check if player has all 3 key relics for Act 4 access."""
        from relics.global_relics.special import RedKey, BlueKey, GreenKey
        
        has_red = any(isinstance(r, RedKey) for r in self.player.relics)
        has_blue = any(isinstance(r, BlueKey) for r in self.player.relics)
        has_green = any(isinstance(r, GreenKey) for r in self.player.relics)
        
        return has_red and has_blue and has_green
    
    def advance_floor(self):
        """
        Advance to next floor within act.
        Returns True if act completed (reached floor 17, boss treasure).
        """
        self.floor_in_act += 1
    
    def advance_act(self) -> bool:
        """
        Advance to next act after boss treasure.
        Returns True if game completed (after act 4 or act 3 without keys).
        Resets act-specific counters and generates new map.
        """
        # Check if can enter act 4
        if self.current_act == 4: # this means act3 finish
            if not self.has_all_keys:
                # No keys - game complete after act 3
                return True
            # Has keys - continue to act 4
        
        if self.current_act > MAX_ACTS:
            return True  # Game complete after act 4
        
        # self.current_act += 1
        # self.floor_in_act = 0
        
        # Reset act-specific counters
        self.normal_encounters_fought = 0
        self.encounter_history = []
        self.elite_history = []
        
        # Reset potion drop chance for new act
        self.potion_drop_chance = 40
        
        # self.initialize_map() # reset map
        
        return False
    
    def initialize_map(self):
        """Initialize map system for current act."""
        from map import MapManager
        
        self.map_manager = MapManager(self.config.seed + self.current_act, act_id=self.current_act)
        self.map_data = self.map_manager.generate_map()

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
            GameStateResult, InputRequestResult, NoneResult
        )

        result = None
        while not self.action_queue.is_empty():
            result = self.action_queue.execute_next()

            # Check if action returned something to process
            if result is not None:
                # Handle legacy returns (Action, List[Action], str) directly
                # for backward compatibility with actions that haven't been updated
                from actions.base import Action

                assert isinstance(result, BaseResult), f"Expected BaseResult, got {type(result)}"
                
                # BaseResult types - handle appropriately
                if isinstance(result, SingleActionResult):
                    self.action_queue.add_action(result.action, to_front=True)
                elif isinstance(result, MultipleActionsResult):
                    self.action_queue.add_actions(result.actions, to_front=True)
                elif isinstance(result, GameStateResult):
                    return result
                elif isinstance(result, InputRequestResult):
                    return result
                # NoneResult: nothing to queue, continue loop
                elif isinstance(result, NoneResult):
                    pass

        return NoneResult()

    def drive_actions(self) -> BaseResult:
        """Run actions until queue drains or the game reaches a terminal state."""
        from utils.result_types import GameStateResult, InputRequestResult, NoneResult

        while True:
            result = self.execute_all_actions()

            if isinstance(result, GameStateResult):
                return result

            if isinstance(result, InputRequestResult):
                submission = self.resolve_input_request(result.request)
                if submission.actions:
                    self.action_queue.add_actions(submission.actions, to_front=True)
                continue

            return result if result is not None else NoneResult()

    def resolve_input_request(self, request: InputRequest) -> InputSubmission:
        """Resolve one declarative input request based on the configured mode."""
        return self.runtime_context.resolve_input_request(request)

    def _augment_human_options(self, request: InputRequest) -> List:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._augment_human_options(request)

    def _resolve_human_selection(self, request: InputRequest) -> List[int]:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._resolve_human_selection(request)

    def _resolve_ai_selection(self, request: InputRequest) -> List[int]:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._resolve_ai_selection(request)

    def _resolve_debug_selection(self, request: InputRequest) -> List[int]:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._resolve_debug_selection(request)

    def _resolve_debug_selection_with_heuristics(
        self,
        options: List,
        actual_max_select: int,
    ) -> Optional[List[int]]:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._resolve_debug_selection_with_heuristics(
            options,
            actual_max_select,
        )

    def _score_debug_option(self, option) -> int:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._score_debug_option(option)

    def _parse_selection_input(
        self,
        raw_input: str,
        option_count: int,
        max_select: int,
        must_select: bool,
    ) -> Optional[List[int]]:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._parse_selection_input(
            raw_input=raw_input,
            option_count=option_count,
            max_select=max_select,
            must_select=must_select,
        )

    def _build_submission(self, options: List, selected_indices: List[int]) -> InputSubmission:
        """Backward-compatible wrapper around runtime selection helpers."""
        return self.runtime_context._build_submission(options, selected_indices)

# Global game state instance
game_state = GameState()

