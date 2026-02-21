"""Deca Boss intentions for Act 3."""

from typing import List

from actions.combat import (
    AttackAction,
    GainBlockAction,
    ApplyPowerAction,
)
from actions.card import AddCardAction
from enemies.intention import Intention
from cards.colorless.dazed import Dazed


class DecaBeam(Intention):
    """Deals 10x2 damage. Adds 2 Dazed into your discard pile."""
    
    def __init__(self, enemy):
        super().__init__("Beam", enemy)
        self.base_damage = 10
        self.base_hits = 2
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        # Add 2 Dazed to discard pile
        for _ in range(2):
            actions.append(AddCardAction(
                card=Dazed(),
                dest_pile="discard_pile",
                source="enemy"
            ))
        
        return actions


class SquareOfProtection(Intention):
    """All enemies gain 16 Block. Gain 1 Plated Armor on A17+."""
    
    def __init__(self, enemy):
        super().__init__("Square of Protection", enemy)
        self.base_block = 16
    
    def execute(self) -> List:
        """Execute the intention - give all enemies block."""
        from engine.game_state import game_state
        
        actions = []
        # Apply Block to all enemies
        for enemy in game_state.enemies:
            if not enemy.is_dead:
                actions.append(GainBlockAction(
                    block=self.base_block,
                    target=enemy
                ))
        
        # On A17+, also gain Plated Armor
        # This is handled by checking ascension in the Deca class
        if hasattr(self.enemy, '_add_plated_armor') and self.enemy._add_plated_armor:
            actions.append(ApplyPowerAction(
                power="plated_armor",
                target=self.enemy,
                amount=1
            ))
        
        return actions