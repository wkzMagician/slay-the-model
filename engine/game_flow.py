"""
Game flow controller - manages to main game loop by iterating over rooms.
Rooms use global action queue for action management.
"""
from rooms.base import Room
from utils.registry import get_registered_instance
from localization import t, LocalStr
from utils.types import RoomType
from engine.game_state import game_state
from utils.result_types import BaseResult, GameStateResult, SingleActionResult


class GameFlow:
    """
    Room-based game flow controller.
    The main loop iterates over rooms, with each room managing its own
    action queue internally. This provides better separation of concerns
    and makes room logic more self-contained.
    """
    MAX_FLOOR = 16  # Maximum floor number (0-16)
    def __init__(self):
        self.current_room = None
    def start_game(self, game_state):
        """
        Start game and run main room loop.
        The loop continues until:
        - Player reaches max floor (WIN)
        - Player dies (DEATH)
        """
        # Display game welcome messages
        self._display_welcome()
        # Initialize map
        game_state.initialize_map()
        # Start with Neo room
        self._start_neo_room()
        
        result = ""
        # Main game loop - iterate over rooms
        while game_state.current_floor < self.MAX_FLOOR:
            # Select next room from map
            cur_room = self._select_next_room(game_state)
            if cur_room is None:
                # No more rooms available
                break
            # Initialize and room
            cur_room.init()
            # Enter room (room uses global action queue)
            result = cur_room.enter()
            # Check for game end conditions
            if isinstance(result, GameStateResult):
                if result.state == "GAME_EXIT":
                    self._handle_game_exit()
                    break
                elif result.state == "GAME_LOSE":
                    self._handle_game_over()
                    break
            elif result == "DEATH":
                self._handle_game_over()
                break
            elif result == "WIN":
                self._handle_game_won()
                break
            
            # Handle MultipleActionsResult from rooms (e.g., combat rewards)
            from utils.result_types import MultipleActionsResult
            if isinstance(result, MultipleActionsResult):
                # Execute the reward actions
                game_state.action_queue.add_actions(result.actions)
                game_state.execute_all_actions()
            
            # Leave the room (cleanup)
            cur_room.leave()

        # If we exited the loop normally, player won by reaching max floor
        if game_state.current_floor >= self.MAX_FLOOR and result != "DEATH":
            self._handle_game_won()
                
    def _display_welcome(self):
        """Display initial game welcome messages"""
        print(f"\n{t('ui.game_welcome', default='Welcome to the Spire!')}")
        print(f"{t('ui.game_awaken', default='You awaken in a strange place...')}")
        print(f"{t('ui.seed_display', seed=game_state.config.seed, default=f'Seed: {game_state.config.seed}')}")
        print(f"{t('ui.character_display', character=game_state.config.character, default=f'Character: {game_state.config.character}')}\n")
    
    def _start_neo_room(self):
        """Start with Neo reward room"""
        neo_room = get_registered_instance("room", "NeoRewardRoom")
        game_state.current_room = neo_room
        game_state.current_floor = 0
        # Initialize and enter Neo room
        assert isinstance(neo_room, Room)
        neo_room.init()
        result = neo_room.enter()
        # Handle Neo room result
        if isinstance(result, GameStateResult) and result.state == "GAME_LOSE":
            self._handle_game_over()
            return
        elif isinstance(result, GameStateResult) and result.state == "GAME_EXIT":
            self._handle_game_exit()
            return
        # Leave Neo room
        neo_room.leave()
        
    def _select_next_room(self, game_state):
        """
        Select and move to the next room from the map.
        Uses SelectMapNodeAction which is pushed to action_queue and executed.
        Returns:
            Room instance for the next room (from game_state.current_room), or None if no moves available.
        """
        # Get available moves from current position
        available_nodes = game_state.map_manager.get_available_moves()
        if not available_nodes:
            # No more moves available
            return None
        
        # Create and push SelectMapNodeAction to action_queue
        from actions.map_selection import SelectMapNodeAction
        select_action = SelectMapNodeAction()
        game_state.action_queue.add_action(select_action)
        
        # Execute all actions in queue (including SelectMapNodeAction)
        game_state.execute_all_actions()
        
        # Return the room from game_state (updated by SelectMapNodeAction.execute())
        return game_state.current_room
    
    def _handle_game_over(self):
        """Handle player death"""
        print(f"\n[X] {t('ui.game_over', default='Game Over! You have fallen in the Spire.')}")
    
    def _handle_game_won(self):
        """Handle player victory"""
        print(f"\n[WIN] {t('ui.game_won', default='Congratulations! You have conquered the Spire!')}")
    
    def _handle_game_exit(self):
        """Handle game exit from menu"""
        print(f"\n[BYE] {t('ui.game_exit', default='Thanks for playing! Goodbye!')}")
