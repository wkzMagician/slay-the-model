"""
Game flow controller - manages the main game loop by iterating over rooms.
Supports multi-act progression (Acts 1-4).
Rooms use global action queue for action management.
"""
from rooms.base import Room
from utils.registry import get_registered_instance
from localization import t, LocalStr
from utils.types import RoomType
from engine.game_state import game_state, FLOORS_PER_ACT, MAX_ACTS
from utils.result_types import BaseResult, GameStateResult, SingleActionResult


class GameFlow:
    """
    Room-based game flow controller with multi-act support.
    
    Each act has 18 floors (0-17):
    - Floor 0: Neo room (Act 1 only)
    - Floors 1-14: Normal rooms
    - Floor 15: Rest site before boss
    - Floor 16: Act boss
    - Floor 17: Boss treasure (hidden, not on map)
    
    After Act 3 boss:
    - Without all 3 keys: Game victory
    - With all 3 keys: Enter Act 4
    
    Act 4 has a shorter structure leading to the Corrupt Heart.
    """
    
    def __init__(self):
        self.current_room = None
    
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
        
        result = ""
        boss_defeated = False
        
        # Act loop - iterate over floors 1-16 (boss is on floor 16, 0-indexed as 15)
        while game_state.floor_in_act < FLOORS_PER_ACT - 1:  # Floors 0-16
            # Check for boss floor (floor_in_act 15 = floor 16 in 1-indexed)
            if game_state.floor_in_act == 15:
                # Boss room
                boss_defeated = self._handle_boss_room(game_state)
                break
            
            # Select next room from map
            cur_room = self._select_next_room(game_state)
            if cur_room is None:
                # No more rooms available
                break
            
            # Initialize and enter room
            cur_room.init()
            result = cur_room.enter()
            
            # Check for game end conditions
            if isinstance(result, GameStateResult):
                if result.state in ("GAME_EXIT",):
                    self._handle_game_exit()
                    return False
                elif result.state in ("GAME_LOSE", "DEATH"):
                    self._handle_game_over()
                    return False
            
            # Handle MultipleActionsResult from rooms
            if isinstance(result, MultipleActionsResult):
                game_state.action_queue.add_actions(result.actions)
                game_state.execute_all_actions()
            
            # Leave the room (cleanup)
            cur_room.leave()
        
        return boss_defeated
    
    def _handle_boss_room(self, game_state) -> bool:
        """Handle boss room encounter. Returns True if boss defeated."""
        from utils.result_types import MultipleActionsResult
        
        # Select boss room from map
        cur_room = self._select_next_room(game_state)
        if cur_room is None:
            return False
        
        # Initialize and enter boss room
        cur_room.init()
        result = cur_room.enter()
        
        # Check for victory (MultipleActionsResult with rewards)
        if isinstance(result, MultipleActionsResult):
            # Boss defeated
            game_state.action_queue.add_actions(result.actions)
            game_state.execute_all_actions()
            cur_room.leave()
            return True
        
        # Check for death
        if isinstance(result, GameStateResult):
            if result.state in ("GAME_LOSE", "DEATH"):
                self._handle_game_over()
                return False
        
        cur_room.leave()
        return False
    
    def _handle_act_completion(self, game_state) -> bool:
        """
        Handle end-of-act: boss treasure room, then act transition.
        Returns True if game should continue to next act.
        """
        from utils.result_types import MultipleActionsResult
        from rooms.treasure import TreasureRoom
        
        # Boss treasure room (Act 1 & 2 have treasure, Act 3 & 4 have victory room)
        if game_state.current_act <= 2:
            # Treasure room for Act 1 and 2
            treasure_room = TreasureRoom(is_boss=True)
            game_state.current_room = treasure_room
            treasure_room.init()
            print(t('rooms.treasure.boss_chest', default='\n=== Boss Treasure Room ==='))
            result = treasure_room.enter()
            
            if isinstance(result, MultipleActionsResult):
                game_state.action_queue.add_actions(result.actions)
                game_state.execute_all_actions()
            
            treasure_room.leave()
        else:
            # Act 3 & 4: Victory/transition room (no treasure)
            print(t('ui.act_complete', act=game_state.current_act, 
                   default=f'\n=== Act {game_state.current_act} Complete! ==='))
        
        # Check if can advance to next act
        if game_state.current_act == 3:
            if not game_state.has_all_keys:
                # No keys - game victory after Act 3
                self._handle_game_won()
                return False
            else:
                # Has all keys - entering Act 4
                print(t('ui.entering_act4', 
                       default='\nWith all three keys, you unlock the path to the Heart...'))
        
        # Advance to next act
        if game_state.advance_act():
            # Game complete (finished Act 4)
            self._handle_game_won()
            return False
        
        # Continue to next act
        print(t('ui.entering_act', act=game_state.current_act, 
               default=f'\n=== Entering Act {game_state.current_act} ==='))
        return True
    
    def _display_welcome(self):
        """Display initial game welcome messages"""
        print(f"\n{t('ui.game_welcome', default='Welcome to the Spire!')}")
        print(f"{t('ui.game_awaken', default='You awaken in a strange place...')}")
        print(f"{t('ui.seed_display', seed=game_state.config.seed, default=f'Seed: {game_state.config.seed}')}")
        print(f"{t('ui.character_display', character=game_state.config.character, default=f'Character: {game_state.config.character}')}\n")
    
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
    
    def _select_next_room(self, game_state):
        """
        Select and create the next room from the map.
        
        Uses the map manager to get available moves and AI decision engine
        to select which room to enter.
        
        Returns:
            Room instance for the selected node, or None if no moves available
        """
        from ai.ai_interface import MockAIDecisionEngine
        from utils.result_types import GameStateResult
        
        # Get available moves from map manager
        available_moves = game_state.map_manager.get_available_moves()
        
        if not available_moves:
            print(t('ui.no_available_moves', default='No available moves on the map.'))
            return None
        
        # Get map context for AI decision
        map_context = game_state.map_manager.get_map_for_ai()
        
        # Display map for human viewing
        game_state.map_manager.display_map_for_human()
        
        # Use AI decision engine to select move
        ai_engine = MockAIDecisionEngine(strategy="first", debug=True)
        try:
            choice_index = ai_engine.make_map_decision(map_context)
        except ValueError:
            return None
        
        # Get the selected node
        selected_node = available_moves[choice_index]
        
        # Create room instance by moving to the selected node
        room = game_state.map_manager.move_to_node(selected_node.floor, selected_node.position)
        
        # Update game state
        game_state.current_room = room
        game_state.advance_floor()
        
        return room
    
    def _handle_game_over(self):
        """Handle player death/game over."""
        print(t('ui.game_over', default='\n=== GAME OVER ==='))
        print(t('ui.death_message', default='You have fallen in the Spire...'))
        print(t('ui.floor_reached', floor=game_state.current_floor, 
               default=f'Floor reached: {game_state.current_floor}'))
    
    def _handle_game_exit(self):
        """Handle game exit."""
        print(t('ui.game_exit', default='\n=== GAME EXIT ==='))
        print(t('ui.exit_message', default='Thanks for playing!'))
    
    def _handle_game_won(self):
        """Handle game victory."""
        print(t('ui.game_won', default='\n=== VICTORY! ==='))
        print(t('ui.victory_message', default='You have conquered the Spire!'))
        print(t('ui.congratulations', default='Congratulations!')) 
