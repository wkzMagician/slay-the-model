"""
Combat state management for storing combat-related information and logic
"""
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from enemies.base import Enemy


class CombatState:
    """Combat state containing all combat-related data"""

    def __init__(self):
        # Orb tracking
        self.orb_history: Dict[str, int] = {}
        self.power_cards_played: int = 0

        # Turn tracking
        self.discarded_cards_this_turn: int = 0
        self.combat_turn: int = 0

        # Turn tracking
        self.turn_cards_played: int = 0
        self.turn_enable_card_play: bool = True
        self.turn_attack_cards_played: int = 0

        # Player turn tracking
        self.player_actions_this_turn: int = 0
        self.player_energy_spent_this_turn: int = 0

        # Phase tracking
        self.current_phase: str = "player_action"  # player_action, enemy_action, player_end
        self.skip_enemy_turn_once: bool = False
        self.preserve_enemy_intent_once: bool = False

        # Blood for Blood tracking
        self.blood_for_blood_hits: int = 0
        self.last_card_targets: List["Enemy"] = []

    def reset_combat_info(self):
        """Reset per-combat counters such as power card tracking and Echo Form flags."""
        self.orb_history = {}
        self.power_cards_played = 0
        self.discarded_cards_this_turn = 0
        self.blood_for_blood_hits = 0
        self.last_card_targets = []

        # Reset turn-specific counters
        self.combat_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0

        # Reset phase
        self.current_phase = "player_action"
        self.skip_enemy_turn_once = False
        self.preserve_enemy_intent_once = False

    def reset_turn_info(self):
        """Reset per-turn counters"""
        self.discarded_cards_this_turn = 0
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
        self.player_actions_this_turn = 0
        self.player_energy_spent_this_turn = 0
        self.turn_enable_card_play = True
        self.last_card_targets = []
