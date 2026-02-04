"""
AI decision engine interface.
Provides the interface for AI-based game decisions.
"""
from typing import Dict, Optional
import json


class AIDecisionEngine:
    """
    Base interface for AI decision making.
    
    This class provides the interface for AI systems to make game decisions.
    It can be extended with specific implementations using LLMs, rule-based systems,
    or other AI approaches.
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize AI decision engine.
        
        Args:
            debug: Whether to enable debug logging
        """
        self.debug = debug
    
    def make_map_decision(self, map_context: Dict) -> int:
        """
        Make a decision about which map node to move to.
        
        Args:
            map_context: Dict containing map information with the following structure:
                - current_floor: Current floor number
                - current_position: Current position on current floor
                - map_ascii: ASCII representation of the map
                - map_json: Structured JSON data
                - available_moves: List of available moves with metadata
                  Each move has: index, floor, position, room_type, risk_level, reward_level
        
        Returns:
            int: The index of the chosen move in the available_moves list (0-based)
        
        Raises:
            ValueError: If no available moves or invalid index returned
        """
        available_moves = map_context.get("available_moves", [])
        
        if not available_moves:
            raise ValueError("No available moves to choose from")
        
        if self.debug:
            self._log_map_context(map_context)
        
        # Default implementation: choose first available move
        # This should be overridden by specific AI implementations
        choice_index = 0
        
        if self.debug:
            print(f"[AI Debug] Choosing move at index {choice_index}:")
            print(f"  Floor: {available_moves[choice_index]['floor']}")
            print(f"  Position: {available_moves[choice_index]['position']}")
            print(f"  Room Type: {available_moves[choice_index]['room_type']}")
            print(f"  Risk Level: {available_moves[choice_index]['risk_level']}")
            print(f"  Reward Level: {available_moves[choice_index]['reward_level']}")
        
        return choice_index
    
    def _log_map_context(self, map_context: Dict):
        """Log map context for debugging"""
        print("[AI Debug] Map Context:")
        print(f"  Current Floor: {map_context['current_floor']}")
        print(f"  Current Position: {map_context['current_position']}")
        print(f"  Available Moves: {len(map_context['available_moves'])}")
        print("\n[AI Debug] ASCII Map:")
        print(map_context['map_ascii'])
        print("\n[AI Debug] Available Moves:")
        for move in map_context['available_moves']:
            print(f"  [{move['index']}] Floor {move['floor']}, Pos {move['position']}: "
                  f"{move['room_type']} (Risk: {move['risk_level']}, Reward: {move['reward_level']})")


class MockAIDecisionEngine(AIDecisionEngine):
    """
    Mock AI decision engine for testing.
    
    This implementation uses simple heuristics for decision making,
    useful for testing without requiring a full LLM integration.
    """
    
    def __init__(self, strategy: str = "first", debug: bool = False):
        """
        Initialize mock AI engine.
        
        Args:
            strategy: Decision strategy ('first', 'last', 'random', 'least_risk', 'highest_reward')
            debug: Whether to enable debug logging
        """
        super().__init__(debug)
        self.strategy = strategy
        import random
        self.random = random.Random()
    
    def make_map_decision(self, map_context: Dict) -> int:
        """
        Make a decision using the configured strategy.
        
        Args:
            map_context: Dict containing map information
            
        Returns:
            int: The index of the chosen move
        """
        available_moves = map_context.get("available_moves", [])
        
        if not available_moves:
            raise ValueError("No available moves to choose from")
        
        if self.debug:
            self._log_map_context(map_context)
        
        if self.strategy == "first":
            choice_index = 0
        
        elif self.strategy == "last":
            choice_index = len(available_moves) - 1
        
        elif self.strategy == "random":
            choice_index = self.random.randint(0, len(available_moves) - 1)
        
        elif self.strategy == "least_risk":
            # Choose move with lowest risk level
            risk_priority = {
                "NONE": 0,
                "LOW": 1,
                "MEDIUM": 2,
                "HIGH": 3,
                "VERY_HIGH": 4,
                "RANDOM": 5
            }
            choice_index = min(
                range(len(available_moves)),
                key=lambda i: risk_priority.get(available_moves[i]['risk_level'], 999)
            )
        
        elif self.strategy == "highest_reward":
            # Choose move with highest reward level
            reward_priority = {
                "NONE": 0,
                "HEAL": 1,
                "SHOP": 2,
                "MEDIUM": 3,
                "HIGH": 4,
                "VERY_HIGH": 5,
                "RANDOM": 1  # Random rewards average to medium
            }
            choice_index = max(
                range(len(available_moves)),
                key=lambda i: reward_priority.get(available_moves[i]['reward_level'], 0)
            )
        
        else:
            # Default to first
            choice_index = 0
        
        if self.debug:
            print(f"[AI Debug] Strategy: {self.strategy}")
            print(f"[AI Debug] Choosing move at index {choice_index}:")
            print(f"  Floor: {available_moves[choice_index]['floor']}")
            print(f"  Position: {available_moves[choice_index]['position']}")
            print(f"  Room Type: {available_moves[choice_index]['room_type']}")
            print(f"  Risk Level: {available_moves[choice_index]['risk_level']}")
            print(f"  Reward Level: {available_moves[choice_index]['reward_level']}")
        
        return choice_index