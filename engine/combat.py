"""
Combat logic class - independent from rooms.
Can be triggered by CombatRoom or Events.
"""
from actions.base import ActionQueue
from actions.display import DisplayTextAction
from engine.game_state import game_state
from localization import Localizable


class Combat(Localizable):
    """
    Combat logic class - handles combat independently from room system.
    
    Can be triggered by:
    - CombatRoom (normal battles)
    - Events (event-based combat)
    """
    
    def __init__(self, enemies: list, is_elite: bool = False, is_boss: bool = False):
        """
        Initialize combat.
        
        Args:
            enemies: List of enemy instances
            is_elite: Whether this is an elite battle
            is_boss: Whether this is a boss battle
        """
        self.enemies = enemies or []
        self.is_elite = is_elite
        self.is_boss = is_boss
        
        # Use local action queue for combat
        self.action_queue = ActionQueue()
        
        # Combat control flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # Localization
        self.localization_prefix = "combat"
    
    def start(self) -> str:
        """
        Start combat execution.
        
        Returns:
            Execution result: None/"DEATH"/"WIN"
        """
        # Initialize combat state
        self._init_combat()
        
        # Display combat start message
        if self.is_boss:
            text_key = "combat.boss_enter"
        elif self.is_elite:
            text_key = "combat.elite_enter"
        else:
            text_key = "combat.enter"
        
        self.action_queue.add_action(DisplayTextAction(text_key=text_key))
        
        # Combat main loop
        while not self.combat_ended:
            # Build turn actions
            self._build_turn_actions()
            
            # Execute actions
            result = self._execute_actions()
            
            # Check if we need to return immediately
            if result in ("DEATH", "WIN"):
                return result
        
        return None
    
    def _init_combat(self):
        """Initialize combat state"""
        # Reset and setup combat state
        game_state.combat_state.reset_combat_info()
        game_state.combat_state.enemies = self.enemies
        game_state.combat_state.is_elite = self.is_elite
        game_state.combat_state.is_boss = self.is_boss
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # Initialize enemies
        for enemy in self.enemies:
            enemy.current_hp = enemy.max_hp
    
    def _build_turn_actions(self):
        """
        Build actions for current turn.
        
        This method should be overridden or extended to build
        turn-specific actions based on game state.
        """
        # Placeholder: subclasses or room implementations will add actions
        # such as PlayCardAction, EnemyIntentAction, etc.
        # todo: 回合逻辑
        pass
    
    def _execute_actions(self) -> str:
        """
        Execute all actions in queue.
        
        Returns:
            Execution result if combat ended, None otherwise
        """
        while not self.action_queue.is_empty() and not self.combat_ended:
            result = self.action_queue.execute_next()
            
            # Check for special return values
            if result in ("DEATH", "WIN"):
                self.combat_ended = True
                return result
            
            # Check if player turn ended (for turn management)
            if result == "turn_ended":
                self.player_turn_ended = True
                # Enemy turn actions would be added here
                self.player_turn_ended = False
        
        return None
    
    def end_combat(self, result: str):
        """
        End combat with specified result.
        
        Args:
            result: Combat result ("WIN" or "DEATH")
        """
        self.combat_ended = True
        return result
    
    def handle_enemy_turn(self):
        """Handle enemy turn actions"""
        # Placeholder: enemy AI logic
        # Add enemy intent actions to queue
        pass
    
    def handle_victory(self):
        """Handle combat victory"""
        # Placeholder: victory rewards
        pass
    
    def handle_defeat(self):
        """Handle combat defeat"""
        # Placeholder: defeat logic
        pass