"""
Combat logic class - independent from rooms.
Can be triggered by CombatRoom or Events.
Uses global action queue for action management.
"""
from collections import Counter
from typing import List
from tui.print_utils import tui_print
from actions.base import Action
from actions.card import DiscardCardAction
from actions.combat import EndTurnAction
from actions.display import DisplayTextAction, SelectAction
from enemies.base import Enemy
from utils.option import Option
from utils.result_types import BaseResult, GameStateResult, NoneResult
from utils.types import CombatType
from localization import LocalStr, Localizable, t

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
        game_state.execute_all_actions()

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
                    actions=[PlayCardAction(card=card)]
                ))
        
        # 3. Build SelectAction for potions
        from actions.combat import UsePotionAction
        for potion in game_state.player.potions:
            if potion.can_be_used_actively:
                options.append(Option(
                    name=LocalStr(potion.info()),
                    actions=[UsePotionAction(potion=potion, target=game_state.player)]
                ))
            
        # 4. Add option to end turn
        options.append(Option(
            name=LocalStr("combat.end_turn"),
            actions=[EndTurnAction()]
        ))
        
        actions.append(SelectAction(
            options=options,
            title=LocalStr("combat.choose_action")
        ))
            
        game_state.action_queue.add_actions(actions)

    def _print_combat_state(self):
        """Print detailed combat state for player feedback"""
        import random
        from engine.game_state import game_state
        from localization import t
        from tui import get_app, is_tui_mode

        # TUI display panel: single-overwrite combat snapshot
        if is_tui_mode():
            app = get_app()
            if app:
                from tui.handlers.display_handler import DisplayHandler
                DisplayHandler(app).display_combat(self, game_state)

        player = game_state.player
        hand = game_state.player.card_manager.get_pile("hand")
        draw_pile = list(game_state.player.card_manager.get_pile("draw_pile"))
        discard_pile = list(game_state.player.card_manager.get_pile("discard_pile"))
        has_frozen_eye = any(
            getattr(relic, "idstr", None) == "FrozenEye"
            for relic in game_state.player.relics
        )

        # Print combat status
        tui_print(f"\n{t('combat.display', default='--- Combat Status ---')}")
        tui_print(f"{t('ui.player_hp', default='HP')}: {player.hp}/{player.max_hp}")
        tui_print(f"{t('ui.player_block', default='Block')}: {player.block}")
        tui_print(f"{t('ui.player_energy', default='Energy')}: {player.energy}/{player.max_energy}")
        
        # Print hand
        tui_print(f"\n{t('ui.hand', default='Hand')} ({len(hand)}):")
        for i, card in enumerate(hand):
            tui_print(f"  [{i+1}] {card.info()}")

        draw_display = list(reversed(draw_pile))
        if not has_frozen_eye:
            random.shuffle(draw_display)
        draw_text = ", ".join(card.display_name.resolve() for card in draw_display)
        discard_text = ", ".join(card.display_name.resolve() for card in discard_pile)
        tui_print(f"\n{t('ui.draw_pile', default='Draw Pile')} ({len(draw_pile)}): {draw_text}")
        tui_print(
            f"{t('ui.discard_pile', default='Discard Pile')} "
            f"({len(discard_pile)}): {discard_text}"
        )
        
        # Print player powers with descriptions
        if player.powers:
            tui_print(f"\n{t('ui.powers', default='Powers')}:")
            for power in player.powers:
                power_name = power.local("name").resolve()
                power_desc = power.local("description", amount=power.amount).resolve() if hasattr(power, 'local') else ""
                # Show duration for powers with amount=None and valid duration
                display_amount = power.amount if power.amount is not None else power.duration
                if display_amount and display_amount > 0:
                    tui_print(f"  {power_name} x{display_amount}")
                else:
                    tui_print(f"  {power_name}")
                # Print description on new line if available and not a raw key
                if power_desc and not power_desc.startswith(power.localization_prefix if hasattr(power, 'localization_prefix') else ""):
                    tui_print(f"    {power_desc}")
        
        # Print enemies state
        tui_print(f"\n{t('combat.enemies', default='=== Enemies ===')}")
        for i, enemy in enumerate(self.enemies):
            enemy_name = enemy.local("name").resolve()
            tui_print(f"\n{enemy_name}:")  # Show enemy name instead of "Enemy 1:"
            tui_print(f"  {t('ui.enemy_hp', default='HP')}: {enemy.hp}/{enemy.max_hp}")
            tui_print(f"  {t('ui.enemy_block', default='Block')}: {enemy.block}")
            
            # Print enemy powers with descriptions
            if enemy.powers:
                tui_print(f"  {t('ui.powers', default='Powers')}:")
                for power in enemy.powers:
                    power_name = power.local("name").resolve()
                    power_desc = power.local("description", amount=power.amount).resolve() if hasattr(power, 'local') else ""
                    # Show duration for powers with amount=None and valid duration
                    display_amount = power.amount if power.amount is not None else power.duration
                    if display_amount and display_amount > 0:
                        tui_print(f"    {power_name} x{display_amount}")
                    else:
                        tui_print(f"    {power_name}")
                    # Print description on new line if available and not a raw key
                    if power_desc and not power_desc.startswith(power.localization_prefix if hasattr(power, 'localization_prefix') else ""):
                        tui_print(f"      {power_desc}")
            
            # Print enemy intention (hidden if player has RunicDome)
            has_runic_dome = any(r.__class__.__name__ == "RunicDome" for r in game_state.player.relics)
            if enemy.current_intention and not has_runic_dome:
                intention = enemy.current_intention
                intention_text = intention.description.resolve()
                tui_print(f"  {t('ui.intention', default='Intention')}: {intention_text}")
        
        tui_print()  # Empty line for readability

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
            game_state.action_queue.add_actions(relic.on_player_turn_end(
                player=game_state.player,
                entities=[e for e in self.enemies if e.hp > 0]
            ))
        # Process player powers: call on_turn_end and remove expired ones
        # tui_print(f"[DEBUG] End of player turn - current powers: {[p.name for p in game_state.player.powers]}")
        powers_to_remove = []
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_end())
            # tui_print(f"[DEBUG] Power {power.name}: duration={power.duration}")
            # Check if power should be removed (duration reached 0)
            if power.duration == 0:
                powers_to_remove.append(power.name)
                # tui_print(f"[DEBUG] Marking power {power.name} for removal")
        
        # Remove expired powers
        for power_name in powers_to_remove:
            game_state.player.remove_power(power_name)
        # tui_print(f"[DEBUG] After power removal - current powers: {[p.name for p in game_state.player.powers]}")
        
        hand = game_state.player.card_manager.get_pile("hand")
        for card in hand:
            game_state.action_queue.add_actions(card.on_player_turn_end())

        # Discard hand (cards in hand are shuffled into discard pile)
        # RunicPyramid: At the end of your turn, you no longer discard your hand.
        from actions.card import ExhaustCardAction
        has_runic_pyramid = any(r.__class__.__name__ == "RunicPyramid" for r in game_state.player.relics)
        if game_state.player.card_manager and not has_runic_pyramid:
            hand = game_state.player.card_manager.get_pile("hand").copy()
            for card in hand:
                game_state.action_queue.add_action(DiscardCardAction(card=card, source_pile="hand"))

        return game_state.execute_all_actions()

    def execute_enemy_phase(self) -> BaseResult:
        """
        Execute enemy phase.

        Returns:
            GameStateResult if combat ends, None otherwise
        """
        from engine.game_state import game_state
        from localization import t

        # Print enemy turn header
        tui_print(f"\n{t('ui.enemy_turn', default='=== Enemy Turn ===')}")

        # DEBUG: Print combat state at start of enemy phase
        # _debug_print_combat_state("ENEMY_PHASE_START", self.enemies)

        self.combat_state.current_phase = "enemy_action"

        # For each alive enemy, execute actions
        for enemy in self.enemies:
            if not enemy.is_dead():
                # Clear block at start of enemy turn (unless Barricade)
                has_barricade = any(p.name == "Barricade" for p in enemy.powers)
                if not has_barricade:
                    enemy.block = 0
                
                # Print enemy intention before executing (hidden if player has RunicDome)
                has_runic_dome = any(r.__class__.__name__ == "RunicDome" for r in game_state.player.relics)
                if not has_runic_dome:
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
                        tui_print(f">> {t('combat.enemy_intends', default='Enemy')} [{enemy_name}] {t('combat.intends_to', default='intends to')}: {intent_desc}")
                game_state.action_queue.add_actions(enemy.execute_intention())

        # Process enemy turn-end effects (tick down power durations)
        self._end_enemy_phase()

        return game_state.execute_all_actions()
    
    def _end_enemy_phase(self):
        """Process end of enemy turn - tick down enemy power durations."""
        from engine.game_state import game_state
        
        # Process each alive enemy's powers
        for enemy in self.enemies:
            if enemy.is_dead():
                continue
                
            # Call on_turn_end for each power and collect actions
            for power in enemy.powers[:]:  # Use slice copy to allow modification
                game_state.action_queue.add_actions(power.on_turn_end())
                
                # Remove power if duration reached 0
                if power.duration == 0:
                    enemy.remove_power(power.name)
    
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
            # Trigger on_combat_end for relics
            for relic in game_state.player.relics:
                game_state.action_queue.add_actions(relic.on_combat_end(
                    player=game_state.player,
                    entities=[e for e in self.enemies if e.hp > 0]
                ))
            
            # Trigger on_combat_end for player powers
            for power in game_state.player.powers:
                game_state.action_queue.add_actions(power.on_combat_end(
                    owner=game_state.player,
                    entities=[e for e in self.enemies if e.hp > 0]
                ))
            
            # Execute all queued actions before returning
            game_state.execute_all_actions()
            
            return GameStateResult("COMBAT_WIN")
        
        # Check if player is dead
        if game_state.player.is_dead():
            # tui_print(f"\n[COMBAT END] GAME_LOSE - Player defeated!")
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
            self._prepare_opening_hand()
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # Clear player powers at start of each combat (powers don't persist between combats)
        game_state.player.powers = []
        
        # Trigger combat start effects (relics)
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_combat_start(
                player=game_state.player,
                entities=[e for e in self.enemies if e.hp > 0]
            ))
        
        # Trigger combat start effects for enemies
        for enemy in self.enemies:
            enemy.on_combat_start(floor=game_state.current_floor)
        
        # God mode: set all enemies to 1 HP if enabled
        god_mode_enabled = game_state.config.get("debug.god_mode", False)
        if god_mode_enabled:
            for enemy in self.enemies:
                enemy.max_hp = 1
                enemy.hp = 1
            game_state.player.max_hp = 10000
            game_state.player.hp = 10000
        
    def _prepare_opening_hand(self):
        """Move innate/bottled cards from draw pile to opening hand."""
        from engine.game_state import game_state

        card_manager = game_state.player.card_manager
        draw_pile = list(card_manager.get_pile("draw_pile"))

        def _bottle_key(card):
            """Key for bottled-card matching: distinguish upgrade levels."""
            card_id = getattr(card, "idstr", card.__class__.__name__)
            upgrade_level = getattr(card, "upgrade_level", 0)
            return (card_id, upgrade_level)

        # 1) Innate cards always start in hand.
        for card in draw_pile:
            if getattr(card, "innate", False):
                card_manager.move_to(card=card, src="draw_pile", dst="hand")

        # 2) Bottled relic cards (if selected) should also start in hand.
        # selected_card references deck-time objects, so match by id+upgrade_level.
        bottled_targets = Counter()
        for relic in game_state.player.relics:
            selected_card = getattr(relic, "selected_card", None)
            if selected_card is None:
                continue
            card_key = _bottle_key(selected_card)
            bottled_targets[card_key] += 1

        if not bottled_targets:
            return

        for card in list(card_manager.get_pile("draw_pile")):
            card_key = _bottle_key(card)
            if bottled_targets[card_key] <= 0:
                continue
            card_manager.move_to(card=card, src="draw_pile", dst="hand")
            bottled_targets[card_key] -= 1

    def _start_player_turn(self):
        """Start player turn - draw cards, reset energy, trigger start-of-turn effects"""
        from engine.game_state import game_state
        from localization import t
        
        # Print player turn header
        tui_print(f"\n{t('ui.player_turn', default='=== Player Turn ===')}")
        
        # Clear block at start of turn (unless Barricade/Calipers)
        has_barricade = any(p.name == "Barricade" for p in game_state.player.powers)
        has_calipers = any(r.idstr == "Calipers" for r in game_state.player.relics)
        
        if has_barricade:
            pass  # Block is not removed
        elif has_calipers:
            game_state.player.block = max(0, game_state.player.block - 15)
        else:
            game_state.player.block = 0

        # Draw cards
        draw_count = game_state.player.draw_count  # modified by relics/powers
        
        # Check for DrawReductionPower - reduce draw count
        draw_reduction = 0
        for power in game_state.player.powers:
            if hasattr(power, 'get_draw_reduction'):
                draw_reduction += power.get_draw_reduction()
        
        draw_count = max(0, draw_count - draw_reduction)

        # First combat turn only: if opening hand already has X cards
        # (e.g., Innate/Bottled), only draw max(Y-X, 0) cards.
        if self.combat_state.combat_turn == 0:
            opening_hand_count = len(game_state.player.card_manager.get_pile("hand"))
            draw_count = max(0, draw_count - opening_hand_count)
        
        if draw_count > 0:
            tui_print(f"\n{t('combat.draw_cards', count=draw_count, default=f'Draw {draw_count} cards')}")
            from actions.card import DrawCardsAction
            game_state.action_queue.add_action(DrawCardsAction(count=draw_count))

        # Reset energy
        game_state.player.energy = game_state.player.max_energy

        # Increment turn counter
        self.combat_state.combat_turn += 1
        self.combat_state.current_phase = "player_action"
        
        # relics - powers
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_player_turn_start(game_state.player, [e for e in self.enemies if e.hp > 0]))
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_start())
        # enemies
        for enemy in self.enemies:
            enemy.on_player_turn_start()
