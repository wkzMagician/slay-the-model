"""
Combat Test Utilities - Provides helpers for systematic card and monster testing.

This module provides utilities to set up real Combat scenarios for testing
cards, monsters, and their interactions in a turn-based combat environment.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Type
from entities.creature import Creature
from enemies.base import Enemy
from cards.base import Card
from player.player import Player
from player.card_manager import CardManager
from engine.combat import Combat
from engine.game_state import GameState
from utils.types import TargetType, CardType
from engine.messages import CardPlayedMessage
class CombatTestHelper:
    """Helper class for setting up and running combat tests."""
    
    def __init__(self):
        """Initialize a fresh combat test environment."""
        self._reset_game_state()
        
    def _reset_game_state(self):
        """Reset game state for a new test."""
        # Reset the EXISTING game_state object instead of creating a new one
        # This ensures all modules that imported game_state see the same object
        from engine import game_state as gs
        gs.game_state.__init__()
        self.game_state = gs.game_state
        self.game_state.player = Player()
        self.game_state.config.mode = "debug"
        self.game_state.config.auto_select = True
        self.game_state.config.debug["select_type"] = "first"
        # Disable god_mode to avoid interference with tests
        self.game_state.config.debug["god_mode"] = False
        # Clear relics and powers to avoid interference with tests
        self.game_state.player.relics = []
        self.game_state.player.powers = []
        
    def create_player(self, hp: int = 80, max_hp: int = 80, energy: int = 3, max_energy: Optional[int] = None) -> Player:
        """Create a fresh player with specified stats."""
        self._reset_game_state()
        player = self.game_state.player
        player.hp = hp
        player.max_hp = max_hp
        player.max_energy = max_energy if max_energy is not None else energy
        player.energy = energy
        player.relics = []  # Clear relics to avoid interference with tests
        return player
    
    def add_card_to_hand(self, card: Card) -> None:
        """Add a card to the player's hand."""
        self.game_state.player.card_manager.piles['hand'].append(card)
        
    def add_card_to_draw_pile(self, card: Card) -> None:
        """Add a card to the player's draw pile."""
        self.game_state.player.card_manager.piles['draw_pile'].append(card)
        
    def add_card_to_discard_pile(self, card: Card) -> None:
        """Add a card to the player's discard pile."""
        self.game_state.player.card_manager.piles['discard_pile'].append(card)
        
    def add_power_to_player(self, power_class, amount: int = 1) -> None:
        """Add a power to the player.
        
        Args:
            power_class: The power class (e.g., StrengthPower) or power name string
            amount: Amount of the power to add
        """
        from powers.definitions import (
            StrengthPower, VulnerablePower, WeakPower, DexterityPower,
            FrailPower, ThornsPower, PoisonPower, BufferPower
        )
        # Map of power names to classes
        POWER_MAP = {
            'Strength': StrengthPower,
            'StrengthPower': StrengthPower,
            'Vulnerable': VulnerablePower,
            'VulnerablePower': VulnerablePower,
            'Weak': WeakPower,
            'WeakPower': WeakPower,
            'Dexterity': DexterityPower,
            'DexterityPower': DexterityPower,
            'Frail': FrailPower,
            'FrailPower': FrailPower,
            'Thorns': ThornsPower,
            'ThornsPower': ThornsPower,
            'Poison': PoisonPower,
            'PoisonPower': PoisonPower,
            'Buffer': BufferPower,
            'BufferPower': BufferPower,
        }
        
        # If string, convert to power class
        if isinstance(power_class, str):
            power_class = POWER_MAP.get(power_class)
            if power_class is None:
                raise ValueError(f"Unknown power: {power_class}")
        
        # Create power instance
        power_instance = power_class(amount=amount)
        
        # Add directly to player using their add_power method
        self.game_state.player.add_power(power_instance)
        
    def create_enemy(self, enemy_class: Type[Enemy], hp: Optional[int] = None) -> Enemy:
        """Create an enemy instance."""
        enemy = enemy_class()
        if hp is not None:
            enemy.max_hp = hp
            enemy.hp = hp
        return enemy
    
    def start_combat(self, enemies: List[Enemy], floor: int = 1) -> Combat:
        """Start a combat with the given enemies.
        
        Args:
            enemies: List of enemy instances
            floor: Current floor number (default 1) - needed for enemy intentions
        """
        # Ensure player exists with no relics to avoid interference
        if not hasattr(self.game_state, 'player') or self.game_state.player is None:
            self.create_player()
        
        # Set floor before combat init - enemies need this for intentions
        self.game_state.current_floor = floor
        
        combat = Combat(enemies=enemies)
        self.game_state.combat = combat
        combat._init_combat()
        return combat
    
    def play_card(self, card: Card, target: Optional[Creature] = None) -> bool:
        """
        Play a card from hand.
        
        Returns True if card was played successfully.
        """
        player = self.game_state.player
        combat = self.game_state.combat
        
        if combat is None:
            raise ValueError("No active combat - call start_combat first")
            
        # Check if card is in hand
        if card not in player.card_manager.piles['hand']:
            raise ValueError(f"Card {card} not in hand")
            
        # Check energy cost (handle X-cost cards where cost = "X")
        cost = card.cost
        from cards.base import COST_X
        if cost == "X" or getattr(card, "_cost", None) == COST_X:
            # X-cost cards use all available energy
            cost = player.energy
            # Store the X-cost value on the card for on_play() to use
            setattr(card, "_x_cost_energy", cost)
        elif cost > player.energy:
            print(f"Not enough energy: need {cost}, have {player.energy}")
            return False
            
        # Spend energy
        player.energy -= cost
        
        # Remove from hand
        player.card_manager.piles['hand'].remove(card)
        
        # Execute card effect
        if card.target_type in (None, TargetType.SELF):
            target = player
        elif target is None:
            if card.target_type in (
                TargetType.ENEMY_SELECT,
                TargetType.ENEMY_RANDOM,
                TargetType.ENEMY_LOWEST_HP,
            ):
                # Default to first enemy for single-target types
                if combat.enemies:
                    target = combat.enemies[0]
            elif card.target_type == TargetType.ENEMY_ALL:
                # For ENEMY_ALL, pass all enemies as targets
                resolved_targets = list(combat.enemies)
                combat.combat_state.last_card_targets = resolved_targets
                card.on_play(resolved_targets)
                self.game_state.publish_message(
                    CardPlayedMessage(
                        card=card,
                        owner=player,
                        targets=resolved_targets,
                    )
                )
                self.game_state.drive_actions()
                card.cost_until_played = None
                # Move to discard or exhaust pile
                if card.exhaust:
                    player.card_manager.piles['exhaust_pile'].append(card)
                else:
                    player.card_manager.piles['discard_pile'].append(card)
                return True
                
        resolved_targets = [target] if target else []
        combat.combat_state.last_card_targets = resolved_targets
        card.on_play(resolved_targets)
        combat.combat_state.turn_cards_played += 1
        if getattr(card, 'card_type', None) == CardType.ATTACK:
            combat.combat_state.turn_attack_cards_played += 1
        self.game_state.publish_message(
            CardPlayedMessage(
                card=card,
                owner=player,
                targets=resolved_targets,
            )
        )
        self.game_state.drive_actions()
        card.cost_until_played = None
                    
        # Only place the card if on_play actions did not already move it.
        if player.card_manager.get_card_location(card) is None:
            if card.exhaust:
                player.card_manager.piles['exhaust_pile'].append(card)
            else:
                player.card_manager.piles['discard_pile'].append(card)
            
        return True
    
    def _execute_actions_recursive(self, actions):
        """Execute actions and drain the global queue after each step."""
        for action in actions:
            if action is None:
                continue
            
            if hasattr(action, 'execute'):
                action.execute()
                self.game_state.drive_actions()
    
    def end_player_turn(self) -> None:
        """End the player's turn and process enemy actions."""
        combat = self.game_state.combat
        if combat:
            combat._end_player_phase()
            
    def execute_enemy_turn(self, enemy: Enemy) -> None:
        """Execute a single enemy's turn."""
        if enemy.current_intention:
            result = enemy.current_intention.execute()
            # Process result if needed
            
    def get_player_block(self) -> int:
        """Get current player block."""
        return self.game_state.player.block
        
    def get_player_hp(self) -> int:
        """Get current player HP."""
        return self.game_state.player.hp
        
    def get_player_powers(self) -> List:
        """Get player's current powers."""
        return self.game_state.player.powers
        
    def get_power_stacks(self, power_name: str) -> int:
        """Get stacks of a specific power on player."""
        for power in self.game_state.player.powers:
            # Check by exact name, with "Power" suffix, or without "Power" suffix
            power_id = power.idstr
            power_base = power_id.replace("Power", "")
            if (power_id == power_name or 
                power.__class__.__name__ == power_name or
                power_base == power_name):
                return power.amount
        return 0
        
    def is_card_in_hand(self, card_name: str) -> bool:
        """Check if a card with given name is in hand."""
        for card in self.game_state.player.card_manager.piles['hand']:
            if card.local("name") == card_name or card.__class__.__name__ == card_name:
                return True
        return False
        
    def is_card_in_discard(self, card_name: str) -> bool:
        """Check if a card with given name is in discard pile."""
        for card in self.game_state.player.card_manager.piles['discard_pile']:
            if card.local("name") == card_name or card.__class__.__name__ == card_name:
                return True
        return False
        
    def is_card_in_exhaust(self, card_name: str) -> bool:
        """Check if a card with given name is in exhaust pile."""
        for card in self.game_state.player.card_manager.piles['exhaust_pile']:
            if str(card.local("name")) == str(card_name) or card.__class__.__name__ == str(card_name):
                return True
        return False
        
    def print_combat_state(self, title: str = "") -> None:
        """Print current combat state for debugging."""
        player = self.game_state.player
        combat = self.game_state.combat
        
        if title:
            print(f"\n=== {title} ===")
            
        print(f"\nPlayer: HP={player.hp}/{player.max_hp}, Block={player.block}, Energy={player.energy}")
        
        powers_str = ", ".join([f"{p.idstr.replace('Power', '')}x{p.amount}" for p in player.powers])
        if powers_str:
            print(f"  Powers: {powers_str}")
            
        hand_str = ", ".join([str(c.local("name")) for c in player.card_manager.piles['hand']])
        print(f"  Hand ({len(player.card_manager.piles['hand'])}): {hand_str}")
        
        discard_str = ", ".join([str(c.local("name")) for c in player.card_manager.piles['discard_pile']])
        print(f"  Discard ({len(player.card_manager.piles['discard_pile'])}): {discard_str}")
        
        exhaust_str = ", ".join([str(c.local("name")) for c in player.card_manager.piles['exhaust_pile']])
        if exhaust_str:
            print(f"  Exhaust ({len(player.card_manager.piles['exhaust_pile'])}): {exhaust_str}")
            
        if combat and combat.enemies:
            print(f"\nEnemies:")
            for enemy in combat.enemies:
                intention_str = ""
                if enemy.current_intention:
                    intention_str = f" -> {enemy.current_intention.description}"
                print(f"  {enemy.__class__.__name__}: HP={enemy.hp}/{enemy.max_hp}, Block={enemy.block}{intention_str}")


def create_test_helper() -> CombatTestHelper:
    """Create a new combat test helper."""
    return CombatTestHelper()
