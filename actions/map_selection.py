"""
Map selection action for choosing next node to visit.
"""
from typing import List, Optional
from actions.base import Action
from actions.display import InputRequestAction
from utils.result_types import BaseResult, NoneResult, SingleActionResult
from map.map_node import MapNode
from utils.option import Option
from localization import BaseLocalStr, LocalStr, t
from typing import List

from utils.registry import register
from tui.print_utils import tui_print

@register("action")
class MoveToMapNodeAction(Action):
    """Move to a specific map node
    
    Required:
        floor (int): Target floor number
        position (int): Target position on that floor
        
    Optional:
        None
        
    Note: In the new architecture, this action only updates the game state.
          The room enter() is called by the GameFlow main loop, not by this action.
    """
    def __init__(self, floor: int, position: int):
        self.floor = floor
        self.position = position
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        # Get map manager
        map_manager = game_state.map_manager
        if not map_manager:
            tui_print("Error: Map not initialized")
            return NoneResult()

        # Move to specified node
        new_room = map_manager.move_to_node(self.floor, self.position)
        
        # Update game state
        game_state.current_room = new_room
        game_state.current_floor = self.floor
        
        # Print which room player moved to
        from localization import t
        tui_print(t("ui.room_entered").format(room_type=new_room.room_type.value, floor=self.floor, position=self.position))
        
        return NoneResult()

@register("action")
class SelectMapNodeAction(Action):
    """
    Action for selecting the next map node to move to.
    
    This action handles both human and AI modes:
    - Human mode: Displays map and presents options for available moves
    - AI mode: Calls the AI decision engine to choose a move
    """
    
    def __init__(self):
        """
        Initialize map selection action.
        """
        pass
        
    
    def execute(self) -> 'BaseResult':
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
            tui_print("\nNo available moves. You've reached end of act!")
            return NoneResult()

        return self._make_decision(map_manager, available_moves)
    
    def _make_decision(self, map_manager, available_moves: List):
        """
        Make decision in human mode by displaying options via InputRequestAction.
        
        This creates a InputRequestAction with options for each available move.
        When the player selects an option, the corresponding MoveToMapNodeAction
        will be executed.
        
        Args:
            map_manager: The MapManager instance
            available_moves: List of available MapNode objects
        """
        from engine.game_state import game_state
        from tui import get_app, is_tui_mode

        # Display map in display-panel for TUI; keep console output for non-TUI
        if is_tui_mode():
            app = get_app()
            if app:
                app.update_player_info(game_state.player, game_state)
                app.update_display_content(map_manager.get_map_text_for_human())
        else:
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
            
        # todo: 在 ai 模式下，获取额外的上下文
        # get_map_context_for_ai
        
        # Return InputRequestAction to be added to caller's action_queue
        select_action = InputRequestAction(
            title=t("ui.select_move", default="Select your next move"),
            options=options
        )
        return SingleActionResult(select_action)
    
    def _get_move_option_name(self, node: MapNode) -> BaseLocalStr:
        """
        Generate a localized name for a move option.
        
        Args:
            node: The MapNode for this move
            
        Returns:
            Localizable string for option name
        """
        # Use localization key for room type
        room_type_key = f"ui.room_type.{node.room_type.value}"
        
        # Build a descriptive option name
        # Format: "Act X - Floor Y, Position Z - RoomType"
        from engine.game_state import game_state
        
        # node.floor is already true floor
        true_floor = node.floor
        
        floor_pos_text = t(
            "ui.floor_position",
            default="Act {act} - Floor {floor}, Position {position}",
            act=game_state.current_act,
            floor=true_floor,
            position=node.position
        )
        room_type_text = t(room_type_key, default=node.room_type.value)
        
        return LocalStr(
            key="ui.map_move_option",
            default="{floor_pos} - {room_type}",
            floor_pos=floor_pos_text,
            room_type=room_type_text
        )
