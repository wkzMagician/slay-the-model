"""
Map selection action for choosing the next node to visit.
"""
from actions.base import Action
from actions.display import SelectAction
from actions.misc import MoveToMapNodeAction
from map.map_node import MapNode
from utils.option import Option
from localization import BaseLocalStr, LocalStr, t
from typing import List


class SelectMapNodeAction(Action):
    """
    Action for selecting the next map node to move to.
    
    This action handles both human and AI modes:
    - Human mode: Displays map and presents options for available moves
    - AI mode: Calls the AI decision engine to choose a move
    """
    
    def __init__(self, ai_engine=None):
        """
        Initialize map selection action.
        
        Args:
            ai_engine: Optional AI decision engine instance. If None and in AI mode,
                      a default MockAIDecisionEngine will be created.
        """
        self.ai_engine = ai_engine
    
    def execute(self):
        """
        Execute map selection action.

        This method:
        1. Gets available moves from map manager
        2. Based on game mode (human/ai), either presents options to player
           or calls AI decision engine
        3. Executes move to selected node
        """
        from engine.game_state import game_state
        # Get available moves
        map_manager = game_state.map_manager
        available_moves = map_manager.get_available_moves()

        if not available_moves:
            print("\nNo available moves. You've reached the end of the act!")
            return

        # Check game mode and handle accordingly
        if game_state.config.mode == "ai":
            # AI mode: Call AI decision engine and execute via action
            choice_index = self._make_ai_decision(map_manager)
            self._execute_move_via_action(available_moves[choice_index])
        else:
            # Human mode: Display map and present options via SelectAction
            self._make_human_decision(map_manager, available_moves)
    
    def _make_human_decision(self, map_manager, available_moves: List):
        """
        Make decision in human mode by displaying options via SelectAction.
        
        This creates a SelectAction with options for each available move.
        When the player selects an option, the corresponding MoveToMapNodeAction
        will be executed.
        
        Args:
            map_manager: The MapManager instance
            available_moves: List of available MapNode objects
        """
        # Display the map
        map_manager.display_map_for_human()
        
        # Create options for each available move
        options = []
        for node in available_moves:
            option_name = self._get_move_option_name(node)
            
            # Create action to move to this node
            move_action = MoveToMapNodeAction(node.floor, node.position)
            
            # Create option with this action
            option = Option(option_name, [move_action])
            options.append(option)
        
        # Return SelectAction to be added to caller's action_queue
        select_action = SelectAction(
            title=t("ui.select_move", default="Select your next move"),
            options=options
        )
        return select_action
    
    def _execute_move_via_action(self, node: MapNode):
        """
        Execute move to selected node by creating MoveToMapNodeAction.
        
        This is used in AI mode where decision is made immediately.
        
        Args:
            node: The MapNode to move to
        """
        # Create MoveToMapNodeAction to return
        move_action = MoveToMapNodeAction(node.floor, node.position)
        return move_action
    
    def _make_ai_decision(self, map_manager) -> int:
        """
        Make decision in AI mode by calling AI decision engine.

        Args:
            map_manager: The MapManager instance

        Returns:
            int: Index of selected move
        """
        # Import AI tools
        from ai_tools.map_tools import get_map_context_for_ai
        from engine.game_state import game_state

        # Get map context for AI
        map_context = get_map_context_for_ai(map_manager)

        # Get or create AI engine
        if self.ai_engine is None:
            # Use MockAIDecisionEngine with default strategy
            from ai.ai_interface import MockAIDecisionEngine
            debug = game_state.config.get('debug', False)
            ai_strategy = game_state.config.get('ai_strategy', 'first')
            self.ai_engine = MockAIDecisionEngine(strategy=ai_strategy, debug=debug)

        # Get AI decision
        choice_index = self.ai_engine.make_map_decision(map_context)

        return choice_index
    
    def _get_move_option_name(self, node: MapNode) -> BaseLocalStr:
        """
        Generate a localized name for a move option.
        
        Args:
            node: The MapNode for this move
            
        Returns:
            Localizable string for the option name
        """
        # Use localization key for room type
        room_type_key = f"ui.room_type.{node.room_type.value}"
        
        # Build a descriptive option name
        # Format: "Floor X, Position Y - RoomType"
        floor_pos_text = t(
            "ui.floor_position",
            default="Floor {floor}, Position {position}",
            floor=node.floor,
            position=node.position
        )
        room_type_text = t(room_type_key, default=node.room_type.value)
        
        return LocalStr(
            key="ui.map_move_option",
            default="{floor_pos} - {room_type}",
            floor_pos=floor_pos_text,
            room_type=room_type_text
        )