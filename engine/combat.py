"""
Combat logic class - independent from rooms.
Can be triggered by CombatRoom or Events.
Uses global action queue for action management.
"""
from actions.display import DisplayTextAction
from localization import Localizable


class Combat(Localizable):
    """
    Combat logic class - handles combat independently from room system.
    
    Can be triggered by:
    - CombatRoom (normal battles)
    - Events (event-based combat)
    Uses the global action queue from game_state for action management.
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
        from engine.game_state import game_state
        
        # Initialize combat state
        self._init_combat()
        
        # Display combat start message
        if self.is_boss:
            text_key = "combat.boss_enter"
        elif self.is_elite:
            text_key = "combat.elite_enter"
        else:
            text_key = "combat.enter"
        
        game_state.action_queue.add_action(DisplayTextAction(text_key=text_key))
        
        # Combat main loop
        while not self.combat_ended:
            # Build turn actions
            self._build_turn_actions()
            
            # Execute actions
            result = self._execute_actions()

            # Check if we need to return immediately
            if result in ("DEATH", "WIN"):
                # Result is already GameStateResult from combat loop
                if isinstance(result, str):
                    from utils.result_types import GameStateResult
                    return GameStateResult(result)
                else:
                    return result
        
        return None
    
    def _init_combat(self):
        """Initialize combat state"""
        from engine.game_state import game_state
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
            # Initialize status effects for enemies
            game_state.combat_state.get_entity_status(enemy)

        # Initialize status effects for player
        game_state.combat_state.get_entity_status(game_state.player)

        # Start first turn
        self._start_player_turn()
    
    def _build_turn_actions(self):
        """
        Build actions for current turn.

        Combat loop: player_action_phase -> enemy_action_phase -> player_end_phase
        """
        from engine.game_state import game_state
        combat_state = game_state.combat_state
        current_phase = combat_state.current_phase

        if current_phase == "player_action":
            # Player action phase - let player play cards
            pass  # Player actions are added externally via PlayCardAction, etc.

        elif current_phase == "enemy_action":
            # Enemy AI phase
            self._enemy_action_phase()

        elif current_phase == "player_end":
            # End of player turn - cleanup
            self._player_end_phase()

    def _start_player_turn(self):
        """Start player turn - draw cards, reset energy"""
        from engine.game_state import game_state
        # Draw cards
        draw_count = game_state.player.max_energy  # Default: draw equal to energy
        if draw_count > 0:
            from actions.combat import DrawCardsAction
            game_state.action_queue.add_action(DrawCardsAction(count=draw_count))
        
        # Reset energy
        game_state.player.energy = game_state.player.max_energy
        
        # Increment turn counter
        game_state.combat_state.combat_turn +=1
        game_state.combat_state.current_phase = "player_action"
        
        # TODO: Trigger on_turn_start powers

    def _player_action_phase(self):
        """Handle player action phase"""
        from engine.game_state import game_state
        # Check if player has no more energy
        if game_state.player.energy <= 0:
            # Transition to enemy action phase
            game_state.combat_state.current_phase = "enemy_action"

    def _enemy_action_phase(self):
        """Handle enemy AI phase"""
        from engine.game_state import game_state
        # Simple AI: each enemy attacks a random valid target
        for enemy in self.enemies:
            if not enemy.is_dead():
                target = self._select_enemy_target(enemy)
                if target:
                    self._enemy_attack(enemy, target)

        # Transition to player end phase
        game_state.combat_state.current_phase = "player_end"

    def _select_enemy_target(self, enemy):
        """Simple AI: select target based on priority"""
        from engine.game_state import game_state
        # Priority: Vulnerable > Normal > most damaged > weakest
        # Default to player
        targets = [game_state.player] + [e for e in self.enemies if not e.is_dead() and e != enemy]

        if not targets:
            return None

        # Priority 1: Vulnerable targets
        vulnerable_targets = [t for t in targets if game_state.combat_state.get_entity_status(t).get("vulnerable", 0) > 0]
        if vulnerable_targets:
            # Among vulnerable targets, pick the one with most damage (lowest HP)
            return min(vulnerable_targets, key=lambda t: t.hp)

        # Priority 2: Normal targets (no vulnerable)
        normal_targets = [t for t in targets if game_state.combat_state.get_entity_status(t).get("vulnerable", 0) == 0]

        if normal_targets:
            # Priority 2a: Most damaged (lowest HP)
            most_damaged = min(normal_targets, key=lambda t: t.hp)
            # If player is to most damaged, attack player
            if most_damaged is game_state.player:
                return most_damaged

            # Priority 2b: Weakest (lowest max HP among most damaged)
            # Get targets with HP within 10% of most damaged
            most_damaged_hp = most_damaged.hp
            damaged_group = [t for t in normal_targets if t.hp <= most_damaged_hp + (most_damaged_hp * 0.1)]

            if damaged_group:
                # Among damaged group, pick the weakest (lowest max HP)
                weakest = min(damaged_group, key=lambda t: t.max_hp)
                return weakest

            # Fallback to most damaged
            return most_damaged

        # Fallback: attack player
        return game_state.player

    def _enemy_attack(self, enemy, target):
        """Execute enemy attack"""
        from engine.game_state import game_state
        # Simple attack: deal damage based on enemy strength
        status = game_state.combat_state.get_entity_status(enemy)
        strength = status.get("strength", 0)
        base_damage = getattr(enemy, "damage", 6) + strength

        # Apply weak if attacker has weak
        attacker_status = game_state.combat_state.get_entity_status(enemy)
        if attacker_status.get("weak", 0) > 0:
            base_damage = int(base_damage * 0.75)
            if base_damage < 1 and getattr(enemy, "damage", 6) > 0:
                base_damage = 1

        # Apply vulnerable (50% more damage to vulnerable targets)
        target_status = game_state.combat_state.get_entity_status(target)
        if target_status.get("vulnerable", 0) > 0:
            base_damage = int(base_damage * 1.5)

        # Deal damage
        damage_dealt = target.take_damage(base_damage, source=enemy, damage_type="direct")

    def _player_end_phase(self):
        """End of player turn - cleanup"""
        from engine.game_state import game_state
        # Discard hand
        from actions.card import ExhaustCardAction
        if game_state.player.card_manager:
            hand = game_state.player.card_manager.get_pile("hand").copy()
            for card in hand:
                game_state.action_queue.add_action(ExhaustCardAction(card=card, source_pile="hand"))
        
        # Reset player block
        game_state.player.block = 0
        
        # Reset status effects that tick down (weak, vulnerable, frail)
        for entity_id, status in game_state.combat_state.status_effects.items():
            for effect in ["weak", "vulnerable", "frail"]:
                if status[effect] > 0:
                    status[effect] -= 1
        
        # Check win/lose conditions
        if game_state.player.is_dead():
            return "DEATH"
        if all(enemy.is_dead() for enemy in self.enemies):
            return "WIN"
        
        # Start new player turn
        self._start_player_turn()

    def _execute_actions(self) -> str:
        """
        Execute all actions in global action queue.
        
        Returns:
            Execution result if combat ended, None otherwise
        """
        from engine.game_state import game_state
        while not game_state.action_queue.is_empty() and not self.combat_ended:
            result = game_state.action_queue.execute_next()
            
            # Check for special return values
            if result in ("DEATH", "WIN"):
                self.combat_ended = True
                return result
            
            # Handle phase transitions
            combat_state = game_state.combat_state
            if combat_state.current_phase == "player_action":
                # Check if player has no energy, trigger phase transition
                if game_state.player.energy <= 0:
                    combat_state.current_phase = "enemy_action"
                    self._build_turn_actions()
            
            elif combat_state.current_phase == "player_end":
                # After end phase actions execute, check win/lose
                if game_state.player.is_dead():
                    return "DEATH"
                if all(enemy.is_dead() for enemy in self.enemies):
                    return "WIN"
                
                # Build actions for next phase
                self._build_turn_actions()
        
        # If queue is empty but combat not ended, check win/lose conditions
        if not self.combat_ended:
            if game_state.player.is_dead():
                return "DEATH"
            if all(enemy.is_dead() for enemy in self.enemies):
                return "WIN"
            
            # Build actions for next phase
            self._build_turn_actions()
        
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