"""Transient enemy intention for Slay the Model."""

from typing import List

from actions.combat import AttackAction
from enemies.intention import Intention
class TransientAttack(Intention):
    """Transient Attack intention - damage scales with turn number."""
    
    def __init__(self, enemy):
        super().__init__("Attack", enemy)
        self.base_damage = 20
    
    def execute(self) -> List:
        """Execute Attack intention - deals 20+N damage where N = turn * 10."""
        current_turn = getattr(self.enemy, '_turn_count', 1)
        
        damage = self.base_damage + (current_turn * 10)
        from engine.game_state import game_state
        from engine.game_state import game_state
        if game_state.ascension >= 17:
            damage = 30 + (current_turn * 10)
        
        return [AttackAction(
            self.enemy.get_damage(damage),
            game_state.player,
            self.enemy,
            "attack"
        )]
