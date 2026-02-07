"""
Game flow controller - manages to main game loop by iterating over rooms.
Rooms use global action queue for action management.
"""
from utils.registry import get_registered_instance
from localization import t, LocalStr
from utils.types import RoomType
from engine.game_state import game_state


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
            if result == "DEATH":
                self._handle_game_over()
                break
            elif result == "WIN":
                self._handle_game_won()
                break
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
        neo_room.init()
        result = neo_room.enter()
        # Handle Neo room result
        if result == "DEATH":
            self._handle_game_over()
            return
        # Leave Neo room
        neo_room.leave()
        
    def _select_next_room(self, game_state):
        """
        Select and move to the next room from the map.
        Returns:
            Room instance for the next room, or None if no moves available
        """
        # Get available moves from current position
        available_nodes = game_state.map_manager.get_available_moves()
        if not available_nodes:
            # No more moves available
            return None
        # Select node based on game mode
        from utils.types import RoomType
        node = None
        if game_state.config.mode == "ai":
            # AI mode: select node with lowest risk (simple heuristic)
            # Priority: REST > SHOP > TREASURE > MONSTER > ELITE
            priority_map = {
                RoomType.REST: 1,
                RoomType.MERCHANT: 2,
                RoomType.TREASURE: 3,
                RoomType.MONSTER: 4,
                RoomType.ELITE: 5,
                RoomType.BOSS: 6,
                RoomType.UNKNOWN: 7,
            }
            # Sort available nodes by room type priority, then by position
            available_nodes.sort(key=lambda n: (
                priority_map.get(n.room_type, 99),
                n.position
            ))
            node = available_nodes[0]
        elif game_state.config.mode == "human":
            # Human mode: prompt user to select
            print(f"\nAvailable moves ({len(available_nodes)}):")
            for idx, move_node in enumerate(available_nodes):
                room_symbol = game_state.map_manager._get_room_symbol(move_node.room_type)
                risk_level = game_state.map_manager._get_risk_level(move_node.room_type)
                reward_level = game_state.map_manager._get_reward_level(move_node.room_type)
                print(f"  [{idx}] Floor {move_node.floor}, Pos {move_node.position} | {room_symbol} | Risk: {risk_level} | Reward: {reward_level}")
            # Prompt for selection
            while True:
                try:
                    from localization import LocalStr
                    prompt = LocalStr(key="ui.select_prompt", default=f"Choose (0-{len(available_nodes)-1}): ")
                    option = int(input(str(prompt)))
                    if 0 <= option < len(available_nodes):
                        node = available_nodes[option]
                        break
                    print(LocalStr(key="ui.invalid_option", default="Invalid option!"))
                except (ValueError, EOFError):
                    print(LocalStr(key="ui.invalid_number", default="Please enter a valid number"))
        else:
            # Default mode: select first available
            node = available_nodes[0]
        # Move to the node and create room
        room = game_state.map_manager.move_to_node(node.floor, node.position)
        # Update game state
        game_state.current_room = room
        game_state.current_floor = node.floor
        return room
    
    def _handle_game_over(self):
        """Handle player death"""
        print(f"\n💀 {t('ui.game_over', default='Game Over! You have fallen in the Spire. 💀')}")
        game_state.game_phase = "game_over"
    
    def _handle_game_won(self):
        """Handle player victory"""
        print(f"\n🎉 {t('ui.game_won', default='Congratulations! You have conquered the Spire! 🎉')}")
        game_state.game_phase = "game_won"
