"""
Combat state management for storing combat-related information and logic
"""
from typing import Dict, Any, Optional


class CombatState:
    """Combat state containing all combat-related data"""
    
    def __init__(self):
        # Orb tracking
        self.orb_history: Dict[str, int] = {}
        self.power_cards_played: int = 0
        
        # Turn tracking
        self.discarded_cards_this_turn: int = 0
        
        # Combat turn tracking
        self.combat_turn: int = 0
        self.turn_cards_played: int = 0
        self.turn_attack_cards_played: int = 0
        
        # enemies
        self.enemies: list = []
        self.is_elite = False
        self.is_boss = False
        
        # Blood for Blood tracking
        self.blood_for_blood_hits: int = 0
    
    def reset_combat_info(self):
        """Reset per-combat counters such as power card tracking and Echo Form flags."""
        self.orb_history = {}
        self.power_cards_played = 0
        self.discarded_cards_this_turn = 0
        self.blood_for_blood_hits = 0
        
        # Reset turn-specific counters
        self.combat_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        
    def reset_turn_info(self):
        self.discarded_cards_this_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0