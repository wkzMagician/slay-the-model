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
        
        # Echo Form tracking
        self.echo_form_next_card_double: bool = False
        self.echo_form_pending_card: Optional[Any] = None
        
        # Turn tracking
        self.discarded_cards_this_turn: int = 0
        self.cards_to_return_to_draw_pile: int = 0
        
        # Card bonuses
        self.card_damage_bonuses: Dict[str, int] = {}
        self.card_block_bonuses: Dict[str, int] = {}
        self.card_cost_reductions: Dict[str, int] = {}
        
        # Pending effects
        self.pending_block: int = 0
        self.pending_energy: int = 0
        
        # Hand retention
        self.retain_hand_this_turn: bool = False
        
        # Combat turn tracking
        self.combat_turn: int = 0
        self.player_turn: bool = True
        self.turn_cards_played: int = 0
        self.turn_attack_cards_played: int = 0
        
        # Current enemies
        self.current_enemies: list = []
        
        # Blood for Blood tracking
        self.blood_for_blood_hits: int = 0
        
        # Game phase
        self.game_phase: str = "exploration"  # "exploration", "combat", "event", "shop", "rest"
    
    def reset_combat_info(self):
        """Reset per-combat counters such as power card tracking and Echo Form flags."""
        self.orb_history = {}
        self.power_cards_played = 0
        self.echo_form_next_card_double = False
        self.echo_form_pending_card = None
        self.discarded_cards_this_turn = 0
        self.cards_to_return_to_draw_pile = 0
        self.card_damage_bonuses = {}
        self.card_block_bonuses = {}
        self.card_cost_reductions = {}
        self.pending_block = 0
        self.pending_energy = 0
        self.retain_hand_this_turn = False
        self.blood_for_blood_hits = 0
        
        # Reset turn-specific counters
        self.combat_turn = 0
        self.player_turn = True
        self.turn_cards_played = 0
        self.turn_attack_cards_played = 0
    
    def reset_turn_info(self):
        """Reset per-turn counters."""
        self.discarded_cards_this_turn = 0
        self.retain_hand_this_turn = False
        self.echo_form_next_card_double = False
        self.echo_form_pending_card = None
    
    def record_orb_generation(self, orb_type: str, amount: int = 1):
        """Track how many of each orb type have been channeled."""
        if not orb_type or amount <= 0:
            return
        self.orb_history[orb_type] = self.orb_history.get(orb_type, 0) + amount
    
    def get_orb_generation_count(self, orb_type: str) -> int:
        """How many of a given orb type were channeled this combat."""
        return self.orb_history.get(orb_type, 0)
    
    def increase_card_damage_bonus(self, card_id: str, amount: int = 0) -> int:
        """Track per-combat damage gains for a specific card."""
        if not card_id or amount == 0:
            return self.card_damage_bonuses.get(card_id, 0)
        try:
            value = int(amount)
        except Exception:
            return self.card_damage_bonuses.get(card_id, 0)
        if value == 0:
            return self.card_damage_bonuses.get(card_id, 0)
        self.card_damage_bonuses[card_id] = self.card_damage_bonuses.get(card_id, 0) + value
        return self.card_damage_bonuses[card_id]
    
    def get_card_damage_bonus(self, card_id: str) -> int:
        """Return the stored damage bonus for a card."""
        return self.card_damage_bonuses.get(card_id, 0)
    
    def increase_card_block_bonus(self, card_id: str, amount: int = 0) -> int:
        """Track per-combat block gains for a specific card."""
        if not card_id or amount == 0:
            return self.card_block_bonuses.get(card_id, 0)
        try:
            value = int(amount)
        except Exception:
            return self.card_block_bonuses.get(card_id, 0)
        if value == 0:
            return self.card_block_bonuses.get(card_id, 0)
        self.card_block_bonuses[card_id] = self.card_block_bonuses.get(card_id, 0) + value
        return self.card_block_bonuses[card_id]
    
    def get_card_block_bonus(self, card_id: str) -> int:
        """Return the stored block bonus for a card."""
        return self.card_block_bonuses.get(card_id, 0)
    
    def increase_card_cost_reduction(self, card_id: str, amount: int = 1) -> int:
        """Track how much the specified card should cost less this combat."""
        if not card_id or amount == 0:
            return self.card_cost_reductions.get(card_id, 0)
        try:
            value = int(amount)
        except Exception:
            return self.card_cost_reductions.get(card_id, 0)
        if value <= 0:
            return self.card_cost_reductions.get(card_id, 0)
        current = self.card_cost_reductions.get(card_id, 0)
        new_value = current + value
        self.card_cost_reductions[card_id] = new_value
        return new_value
    
    def get_card_cost_reduction(self, card_id: str) -> int:
        """Return how much the given card's cost should be reduced."""
        if not card_id:
            return 0
        return self.card_cost_reductions.get(card_id, 0)
    
    def reset_card_cost_reductions(self):
        """Clear per-card cost reductions at the start of combat."""
        self.card_cost_reductions = {}
    
    def reset_card_damage_bonuses(self):
        """Clear stored damage bonuses for cards at the start of combat."""
        self.card_damage_bonuses = {}
    
    def reset_card_block_bonuses(self):
        """Clear stored block bonuses for cards at the start of combat."""
        self.card_block_bonuses = {}
    
    def enable_echo_form_for_next_card(self):
        """Mark the next non-clone card as eligible for Echo Form duplication."""
        self.echo_form_pending_card = None
        self.echo_form_next_card_double = True
    
    def apply_pending_block(self) -> int:
        """Grant any pending block scheduled for the start of this turn."""
        if self.pending_block <= 0:
            return 0
        block_amount = self.pending_block
        self.pending_block = 0
        return block_amount
    
    def apply_pending_energy(self) -> int:
        """Grant any pending energy scheduled for the start of this turn."""
        if self.pending_energy <= 0:
            return 0
        energy_amount = self.pending_energy
        self.pending_energy = 0
        return energy_amount