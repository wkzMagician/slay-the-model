"""
Combat state management for storing combat-related information and logic
"""
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from enemies.base import Enemy


class CombatState:
    """Combat state containing all combat-related data"""

    def __init__(self):
        # Enemy tracking
        self.enemies: List['Enemy'] = []
        
        # Orb tracking
        self.orb_history: Dict[str, int] = {}
        self.power_cards_played: int = 0

        # Turn tracking
        self.discarded_cards_this_turn: int = 0

        # Combat turn tracking
        self.combat_turn: int = 0
        self.turn_cards_played: int = 0
        self.turn_attack_cards_played: int = 0

        # Player turn tracking
        self.player_actions_this_turn: int = 0
        self.player_energy_spent_this_turn: int = 0

        # Phase tracking
        self.current_phase: str = "player_action"  # player_action, enemy_action, player_end

        # Blood for Blood tracking
        self.blood_for_blood_hits: int = 0

    def add_enemy(self, enemy: 'Enemy') -> None:
        """Add an enemy to combat.
        
        Args:
            enemy: Enemy instance to add
        """
        if enemy not in self.enemies:
            self.enemies.append(enemy)
    
    def remove_enemy(self, enemy: 'Enemy') -> None:
        """Remove an enemy from combat.
        
        Args:
            enemy: Enemy instance to remove
        """
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def reset_combat_info(self):
        """Reset per-combat counters such as power card tracking and Echo Form flags."""
        self.enemies.clear()
        
        self.orb_history = {}
        self.power_cards_played = 0
        self.discarded_cards_this_turn = 0
        self.blood_for_blood_hits = 0

        # Reset turn-specific counters
        self.combat_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0

        # Reset phase
        self.current_phase = "player_action"

    def reset_turn_info(self):
        """Reset per-turn counters"""
        self.discarded_cards_this_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0