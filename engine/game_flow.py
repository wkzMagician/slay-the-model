"""
Game flow controller - manages the main game loop by iterating over rooms.
Supports multi-act progression (Acts 1-4).
Rooms use global action queue for action management.
"""
from rooms.base import Room
from utils.registry import get_registered_instance
from localization import t, LocalStr
from utils.types import RoomType
from engine.game_state import game_state, MAX_ACTS
from utils.result_types import BaseResult, GameStateResult, SingleActionResult
from tui.print_utils import tui_print


class GameFlow:
    """
    Room-based game flow controller with multi-act support.
    
    Floor layout varies by act:
    - Act 1-2: 18 floors (0-17), floor 16=boss, floor 17=treasure
    - Act 3 (A<20): 18 floors (0-17), floor 16=boss, floor 17=VictoryRoom
    - Act 3 (A20): 19 floors (0-18), floor 16=boss1, floor 17=boss2, floor 18=VictoryRoom
    - Act 4: 6 floors (0-5), fixed: Rest->Shop->Elite->Boss->VictoryRoom
    
    VictoryRoom handles key checking for Act 4 transition.
    """
    
    def __init__(self):
        self.current_room = None
    
    def _get_max_floor(self, game_state) -> int:
        """Get the maximum floor number for current act (0-indexed)."""        
        if game_state.current_act == 4:
            return 5  # Act 4: 6 floors (0-5)
        elif game_state.current_act == 3 and game_state.ascension >= 20:
            return 18  # Act 3 A20: 19 floors (0-18)
        else:
            return 17  # Default: 18 floors (0-17)
    
    def start_game(self, game_state):
        """
        Start game and run main game loop across all acts.
        The loop continues until:
        - Player defeats final boss (WIN)
        - Player dies (DEATH)
        """
        # Display game welcome messages
        self._display_welcome()
        
        # Main act loop
        while game_state.current_act <= MAX_ACTS:
            # Initialize map for current act
            game_state.initialize_map()
            
            # Start with Neo room (Act 1 only)
            if game_state.current_act == 1:
                self._start_neo_room()
            
            # Run this act
            boss_defeated = self._run_act(game_state)
            
            if not boss_defeated:
                # Player died during act
                break
            
            # Handle act completion (boss treasure, act transition)
            should_continue = self._handle_act_completion(game_state)
            
            if not should_continue:
                # Game complete (no keys for act 4, or finished act 4)
                break
        
    def _run_act(self, game_state) -> bool:
        """
        Run a single act from current floor to boss.
        Returns True if boss defeated, False if player died.
        """
        from utils.result_types import MultipleActionsResult
        from rooms.victory import VictoryRoom
        
        result = ""
        # max_floor = self._get_max_floor(game_state)
        current_act = game_state.current_act
        
        # Act loop - iterate over floors up to max_floor
        while game_state.current_act == current_act:
            # Select next room from map
            cur_room = self._select_next_room(game_state)
            if cur_room is None:
                # No more rooms available
                break
            
            # Initialize and enter room
            cur_room.init()
            result = cur_room.enter()

            # Update display panel with room content
            from tui import get_app, is_tui_mode
            if is_tui_mode():
                app = get_app()
                if app:
                    from tui.handlers.display_handler import DisplayHandler
                    DisplayHandler(app).display_room(cur_room, game_state)
            
            # Check for game end conditions
            if isinstance(result, GameStateResult):
                if result.state in ("GAME_EXIT",):
                    self._handle_game_exit()
                    return False
                elif result.state in ("GAME_LOSE", "DEATH"):
                    self._handle_game_over()
                    return False
            
            # Handle results from rooms
            if isinstance(result, MultipleActionsResult):
                game_state.action_queue.add_actions(result.actions)
                game_state.execute_all_actions()
            elif isinstance(result, SingleActionResult):
                game_state.action_queue.add_action(result.action, to_front=True)
                game_state.execute_all_actions()
            
            # Leave the room (cleanup)
            cur_room.leave()
            
            # Check if VictoryRoom was entered and handled completion
            if isinstance(cur_room, VictoryRoom):
                # VictoryRoom handles its own completion
                return True
        
        return True
    
    def _handle_act_completion(self, game_state) -> bool:
        """
        Handle end-of-act: boss treasure room (Acts 1-2), then act transition.
        VictoryRoom (Acts 3-4) handles its own completion via the room itself.
        Returns True if game should continue to next act.
        """
        from utils.result_types import MultipleActionsResult
        from rooms.treasure import TreasureRoom
        
        # Check if can advance to next act
        if game_state.current_act == 4: # this means act3 finish!
            if not game_state.has_all_keys:
                # No keys - game victory after Act 3
                self._handle_game_won()
                return False
            else:
                # Has all keys - entering Act 4
                tui_print(t('ui.entering_act4', 
                       default='\nWith all three keys, you unlock the path to the Heart...'))
        
        # Advance to next act
        if game_state.advance_act():
            # Game complete (finished Act 4)
            self._handle_game_won()
            return False
        
        # Continue to next act
        tui_print(t('ui.entering_act', act=game_state.current_act, 
               default=f'\n=== Entering Act {game_state.current_act} ==='))
        return True
    
    def _display_welcome(self):
        """Display initial game welcome messages"""
        tui_print(f"\n{t('ui.game_welcome', default='Welcome to the Spire!')}")
        tui_print(f"{t('ui.game_awaken', default='You awaken in a strange place...')}")
        tui_print(f"{t('ui.seed_display', seed=game_state.config.seed, default=f'Seed: {game_state.config.seed}')}")
        tui_print(f"{t('ui.character_display', character=t(f'ui.character.{game_state.config.character.lower()}', default=game_state.config.character), default=f'Character: {game_state.config.character}')}\n")

        # Update display panel with player info
        from tui import get_app, is_tui_mode
        if is_tui_mode():
            app = get_app()
            if app:
                app.update_player_info(game_state.player, game_state)
    
    def _start_neo_room(self):
        """Start with Neo reward room (Act 1 only)"""
        neo_room = get_registered_instance("room", "NeoRewardRoom")
        game_state.current_room = neo_room
        game_state.current_floor = 0  # This sets act=1, floor_in_act=0
        # Initialize and enter Neo room
        assert isinstance(neo_room, Room)
        neo_room.init()
        result = neo_room.enter()
        # Handle Neo room result
        if isinstance(result, GameStateResult) and result.state == "GAME_LOSE":
            self._handle_game_over()
            return
        neo_room.leave()
    
    def _select_next_room(self, game_state):
        """
        Select and create the next room from the map.
        
        Uses SelectMapNodeAction to handle player choice.
        
        Returns:
            Room instance for the selected node, or None if no moves available
        """
        from actions.map_selection import SelectMapNodeAction
        
        # Use SelectMapNodeAction to handle selection
        select_action = SelectMapNodeAction()
        result = select_action.execute()
        
        # The SelectMapNodeAction will return a MoveToMapNodeAction wrapped in SingleActionResult
        # We need to add it to queue and execute
        if isinstance(result, SingleActionResult):
            game_state.action_queue.add_action(result.action)
            game_state.execute_all_actions()
        
        # After execution, get the current room from game_state
        room = game_state.current_room
        
        return room
    
    def _handle_game_over(self):
        """Handle player death/game over."""
        tui_print(t('ui.game_over', default='\n=== GAME OVER ==='))
        tui_print(t('ui.death_message', default='You have fallen in the Spire...'))
        tui_print(t('ui.floor_reached', floor=game_state.current_floor, 
               default=f'Floor reached: {game_state.current_floor}'))
    
    def _handle_game_exit(self):
        """Handle game exit."""
        tui_print(t('ui.game_exit', default='\n=== GAME EXIT ==='))
        tui_print(t('ui.exit_message', default='Thanks for playing!'))
    
    def _handle_game_won(self):
        """Handle game victory."""
        tui_print(t('ui.game_won', default='\n=== VICTORY! ==='))
        tui_print(t('ui.victory_message', default='You have conquered the Spire!'))
        tui_print(t('ui.congratulations', default='Congratulations!'))
