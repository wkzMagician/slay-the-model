"""Dagger minion intentions for Slay the Model."""

from typing import List

from actions.combat import AttackAction, RemoveEnemyAction
from enemies.intention import Intention


class WoundIntention(Intention):
    """Dagger Wound intention - deals damage and adds Wound."""
    
    def __init__(self, enemy):
        super().__init__("Wound", enemy)
        self.base_damage = 9
    
    def execute(self) -> List:
        """Execute Wound intention."""
        from cards.status import Wound
        from engine.game_state import game_state
        
        # Add Wound to player's discard pile
        game_state.player.discard_pile.append(Wound())
        
        return [AttackAction(
            self.enemy.get_damage(self.base_damage),
            game_state.player,
            self.enemy,
            "attack"
        )]


class ExplodeIntention(Intention):
    """Dagger Explode intention - deals damage and dies."""
    
    def __init__(self, enemy):
        super().__init__("Explode", enemy)
        self.base_damage = 25
    
    def execute(self) -> List:
        """Execute Explode intention."""
        from engine.game_state import game_state
        
        return [
            AttackAction(
                self.base_damage,
                game_state.player,
                self.enemy,
                "attack"
            ),
            RemoveEnemyAction(self.enemy)
        ]
