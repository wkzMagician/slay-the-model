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

        # Player turn tracking
        self.player_actions_this_turn: int = 0
        self.player_energy_spent_this_turn: int = 0

        # Phase tracking
        self.current_phase: str = "player_action"  # player_action, enemy_action, player_end

        # Status effects for player and enemies
        # Format: {entity_id: {"weak": amount, "vulnerable": amount, "frail": amount, "strength": amount}}
        self.status_effects: Dict[str, Dict[str, int]] = {}

        # enemies
        self.enemies: list = []
        self.is_elite = False
        self.is_boss = False

        # Blood for Blood tracking
        self.blood_for_blood_hits: int = 0

    def get_entity_status(self, entity) -> Dict[str, int]:
        """Get status effects for an entity"""
        entity_id = id(entity)
        if entity_id not in self.status_effects:
            self.status_effects[entity_id] = {
                "weak": 0,
                "vulnerable": 0,
                "frail": 0,
                "strength": 0
            }
        return self.status_effects[entity_id]

    def apply_status(self, entity, status_type: str, amount: int) -> None:
        """Apply status effect to an entity"""
        if amount == 0:
            return

        entity_id = id(entity)
        if entity_id not in self.status_effects:
            self.status_effects[entity_id] = {
                "weak": 0,
                "vulnerable": 0,
                "frail": 0,
                "strength": 0
            }

        status = self.status_effects[entity_id]
        if status_type in status:
            status[status_type] = max(0, status[status_type] + amount)

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
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0

        # Reset phase
        self.current_phase = "player_action"

        # Clear all status effects
        self.status_effects = {}

    def reset_turn_info(self):
        """Reset per-turn counters"""
        self.discarded_cards_this_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0