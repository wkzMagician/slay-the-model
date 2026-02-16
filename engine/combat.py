"""
Combat logic class - independent from rooms.
Can be triggered by CombatRoom or Events.
Uses global action queue for action management.
"""
from typing import List
from actions.base import Action
from actions.card import DiscardCardAction
from actions.combat import EndTurnAction
from actions.display import DisplayTextAction, SelectAction
from enemies.base import Enemy
from utils.option import Option
from utils.result_types import BaseResult, GameStateResult, NoneResult
from utils.types import CombatType
from localization import LocalStr, Localizable

class Combat(Localizable):
    """
    Combat logic class - handles combat independently from room system.

    Can be triggered by:
    - CombatRoom (normal battles)
    - Events (event-based combat)
    Uses global action queue from game_state for action management.
    """

    def __init__(self, enemies: List[Enemy], combat_type: CombatType = CombatType.NORMAL):
        """
        Initialize combat.

        Args:
            enemies: List of enemy instances
            combat_type: Type of combat (Normal/Elite/Boss), used for relic effects
        """
        self.enemies = enemies
        self.combat_type = combat_type
        
        # Combat state
        from .combat_state import CombatState
        self.combat_state = CombatState()
        
        # Combat control flags
        self.combat_ended = False
        self.player_turn_ended = False

    def add_enemy(self, enemy: Enemy):
        """Add an enemy to combat."""
        if enemy not in self.enemies:
            self.enemies.append(enemy)

    def remove_enemy(self, enemy: Enemy):
        """Remove an enemy from combat (e.g., when killed)."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        
        # Localization
        self.localization_prefix = "combat"

    def start(self) -> GameStateResult:
        """
        Start combat execution.

        Returns:
            Execution result: WIN / LOSE / ESCAPE
        """
        from engine.game_state import game_state

        # Initialize combat state
        self._init_combat()

        # Display combat start message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="combat.enter"
        ))

        # Combat main loop (as per todo.md)
        while True:
            # Execute player phase
            result = self.execute_player_phase()
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                break

            # Execute enemy phase
            result = self.execute_enemy_phase()
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                break

        return result

    def execute_player_phase(self) -> BaseResult:
        """
        Execute player phase.

        Returns:
            GameStateResult if combat ends, NoneResult otherwise
        """
        from engine.game_state import game_state

        # Start player phase: gain energy, draw cards, trigger start-of-turn effects
        self._start_player_turn()
        
        # Execute draw cards and start-of-turn effects immediately
        # This ensures hand is populated before building player actions
        result = game_state.execute_all_actions()
        if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
            return result
                
        # Check for combat end (e.g., all enemies dead from start-of-turn effects)
        result = self._check_combat_end()
        if isinstance(result, GameStateResult):
            return result

        # Player action phase - wait for player to play cards, use potions, or end turn
        self.combat_state.current_phase = "player_action"

        while self.combat_state.current_phase == "player_action":
            # Print detailed combat state for player feedback
            self._print_combat_state()

            self._build_player_action()

            result = game_state.execute_all_actions()
            
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                return result
            
            # Check for combat end (e.g., all enemies dead from card damage)
            result = self._check_combat_end()
            if isinstance(result, GameStateResult):
                return result

        # End player phase: trigger end-of-turn effects, discard hand
        return self._end_player_phase()
    
    def _build_player_action(self):
        """Build available player actions during player phase"""
        from engine.game_state import game_state
        actions = []

        # 1. Display combat information
        from localization import t, LocalStr
        from utils.types import CombatType

        # Get player info
        player = game_state.player
        enemies = self.enemies

        # Build status string
        status_parts = []
        status_parts.append(f"{t('ui.player_hp', default='Player HP')}: {player.hp}/{player.max_hp}")
        status_parts.append(f"{t('ui.player_block', default='Block')}: {player.block}")
        status_parts.append(f"{t('ui.player_energy', default='Energy')}: {player.energy}/{player.max_energy}")

        # Get enemy info
        for enemy in enemies:
            status_parts.append(f"{t('ui.enemy_hp', default='Enemy HP')}: {enemy.hp}/{enemy.max_hp}")
            status_parts.append(f"{t('ui.enemy_block', default='Block')}: {enemy.block}")

        actions.append(DisplayTextAction(text_key="combat.display"))

        # 2. Build SelectAction for cards in hand
        
        # 2. Build SelectAction for cards in hand
        hand = game_state.player.card_manager.get_pile("hand")
        options: List[Option] = []
        for card in hand:
            # can_play returns tuple (bool, Optional[str])
            can_play_result, reason = card.can_play()
            if can_play_result:
                # Use PlayCardAction to properly handle energy cost and card removal
                from actions.combat import PlayCardAction
                options.append(Option(
                    name=card.info(),
                    actions=[PlayCardAction(card=card, is_auto=True)]
                ))
        
        # 3. Build SelectAction for potions (if implemented)
        for potion in game_state.player.potions:
            options.append(Option(
                name=LocalStr(potion.info()),
                actions=potion.on_use()
            ))
            
        # 4. Add option to end turn
        options.append(Option(
            name=LocalStr("combat.end_turn"),
            actions=[EndTurnAction()]
        ))
        
        actions.append(SelectAction(
            options=options,
            prompt=LocalStr("combat.choose_action")
        ))
            
        game_state.action_queue.add_actions(actions)

    def _print_combat_state(self):
        """Print detailed combat state for player feedback"""
        from engine.game_state import game_state
        from localization import t
        
        player = game_state.player
        hand = game_state.player.card_manager.get_pile("hand")
        
        # Print player state
        print(f"\n=== {t('ui.player_turn', default='Player Turn')} ===")
        print(f"{t('ui.player_hp', default='HP')}: {player.hp}/{player.max_hp}")
        print(f"{t('ui.player_block', default='Block')}: {player.block}")
        print(f"{t('ui.player_energy', default='Energy')}: {player.energy}/{player.max_energy}")
        
        # Print hand
        print(f"\n{t('ui.hand', default='Hand')} ({len(hand)}):")
        for i, card in enumerate(hand):
            print(f"  [{i+1}] {card.info()}")
        
        # Print player powers
        if player.powers:
            print(f"\n{t('ui.powers', default='Powers')}:")
            for power in player.powers:
                power_name = power.local("name").resolve()
                if power.amount > 0:
                    print(f"  {power_name} x{power.amount}")
                else:
                    print(f"  {power_name}")
        
        # Print enemies state
        print(f"\n=== {t('combat.enemies', default='Enemies')} ===")
        for i, enemy in enumerate(self.enemies):
            print(f"\n{t('ui.enemy', default='Enemy')} {i+1}:") # todo: 显示 name
            print(f"  {t('ui.enemy_hp', default='HP')}: {enemy.hp}/{enemy.max_hp}")
            print(f"  {t('ui.enemy_block', default='Block')}: {enemy.block}")
            
            # Print enemy powers
            if enemy.powers:
                print(f"  {t('ui.powers', default='Powers')}:")
                for power in enemy.powers:
                    power_name = power.local("name").resolve()
                    if power.amount > 0:
                        print(f"    {power_name} x{power.amount}")
                    else:
                        print(f"    {power_name}")
            
            # Print enemy intention
            if enemy.current_intention:
                intention = enemy.current_intention
                intention_text = intention.description.resolve()
                print(f"  {t('ui.intention', default='Intention')}: {intention_text}")
        
        print()  # Empty line for readability

    def _end_player_phase(self) -> BaseResult:
        """
        End player phase.

        Returns:
            GameStateResult if combat ends, None otherwise
        """
        from engine.game_state import game_state

         # Trigger end-of-turn effects
        # relics - powers - cards in hand
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_player_turn_end())
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_end())
        
        hand = game_state.player.card_manager.get_pile("hand")
        for card in hand:
            game_state.action_queue.add_actions(card.on_player_turn_end())

        # Discard hand (cards in hand are shuffled into discard pile)
        from actions.card import ExhaustCardAction
        if game_state.player.card_manager:
            hand = game_state.player.card_manager.get_pile("hand").copy()
            for card in hand:
                game_state.action_queue.add_action(DiscardCardAction(card=card, source_pile="hand"))

        # Reset player block
        game_state.player.block = 0

        return game_state.execute_all_actions()

    def execute_enemy_phase(self) -> BaseResult:
        """
        Execute enemy phase.

        Returns:
            GameStateResult if combat ends, None otherwise
        """
        from engine.game_state import game_state

        # DEBUG: Print combat state at start of enemy phase
        # _debug_print_combat_state("ENEMY_PHASE_START", self.enemies)

        self.combat_state.current_phase = "enemy_action"

        # For each alive enemy, execute actions
        for enemy in self.enemies:
            if not enemy.is_dead():
                # Print enemy intention before executing
                enemy_name_raw = enemy.local("name").resolve() if hasattr(enemy, 'local') else 'Enemy'
                # Extract readable name from localization key (e.g., "Cultist" from "enemies.Cultist.name")
                if enemy_name_raw.startswith("enemies."):
                    enemy_name = enemy_name_raw.split(".")[1] if len(enemy_name_raw.split(".")) > 1 else enemy_name_raw
                else:
                    enemy_name = enemy_name_raw
                intent_desc_raw = enemy.current_intention.description.resolve() if hasattr(enemy, 'current_intention') and hasattr(enemy.current_intention, 'description') else ''
                # Extract readable description from localization key
                if intent_desc_raw.startswith("enemies."):
                    intent_desc = intent_desc_raw.split(".")[-1] if "." in intent_desc_raw else intent_desc_raw
                else:
                    intent_desc = intent_desc_raw
                if intent_desc:
                    print(f">> Enemy [{enemy_name}] intends to: {intent_desc}")
                game_state.action_queue.add_actions(enemy.execute_intention())

        return game_state.execute_all_actions()
    
    def _remove_dead_enemies(self):
        """Remove dead enemies from the list"""
        self.enemies = [e for e in self.enemies if not e.is_dead()]
    
    def _check_combat_end(self) -> BaseResult:
        """Check if combat should end.
        
        Returns:
            GameStateResult("COMBAT_WIN") if all enemies are dead,
            GameStateResult("COMBAT_LOSE") if player is dead,
            NoneResult otherwise
        """
        from engine.game_state import game_state
        
        # Remove dead enemies first
        self._remove_dead_enemies()
        
        # Check if all enemies are dead
        if not self.enemies or all(e.is_dead() for e in self.enemies):
            print(f"\n[COMBAT END] COMBAT_WIN - All enemies defeated!")
            return GameStateResult("COMBAT_WIN")
        
        # Check if player is dead
        if game_state.player.is_dead():
            print(f"\n[COMBAT END] GAME_LOSE - Player defeated!")
            return GameStateResult("GAME_LOSE")
        
        return NoneResult()
    
    def _init_combat(self):
        """Initialize combat state"""
        from engine.game_state import game_state
        
        # Set current combat reference
        game_state.current_combat = self
        
        # Reset and setup combat state
        self.combat_state.reset_combat_info()
        
        # Reset card manager for combat (initialize draw pile from deck)
        if hasattr(game_state.player, 'card_manager'):
            game_state.player.card_manager.reset_for_combat()
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # Trigger combat start effects (relics)
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_combat_start(
                player=game_state.player,
                entities=self.enemies
            ))
        
        # Trigger combat start effects for enemies
        for enemy in self.enemies:
            enemy.on_combat_start(floor=game_state.current_floor)
        
        # God mode: apply 999 BufferPower if enabled
        if game_state.config.get("debug.god_mode", False):
            from powers.definitions.buffer import BufferPower
            game_state.player.add_power(BufferPower(amount=999, owner=game_state.player))
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # todo: prepare innate cards to top of draw_pile

    def _start_player_turn(self):
        """Start player turn - draw cards, reset energy, trigger start-of-turn effects"""
        from engine.game_state import game_state
        # Draw cards
        draw_count = game_state.player.draw_count  # todo: modified by relics/powers
        if draw_count > 0:
            from actions.card import DrawCardsAction
            game_state.action_queue.add_action(DrawCardsAction(count=draw_count))

        # Reset energy
        game_state.player.energy = game_state.player.max_energy

        # Increment turn counter
        self.combat_state.combat_turn += 1
        self.combat_state.current_phase = "player_action"
        
        # relics - powers
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_player_turn_start())
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_start())
        # enemies
        for enemy in self.enemies:
            enemy.on_player_turn_start()