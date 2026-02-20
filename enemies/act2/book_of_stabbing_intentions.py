"""Book of Stabbing intentions - Act 2 Elite enemy."""

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction
from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.book_of_stabbing import BookOfStabbing


class MultiStab(Intention):
    """Deals 6×N damage where N increases each use."""
    
    def __init__(self, enemy: "BookOfStabbing"):
        super().__init__("Multi Stab", enemy)
        self.base_damage = 6  # Per hit
        self._hits_base = 2  # Base number of hits
    
    def execute(self) -> List:
        """Execute multi-stab attack."""
        from engine.game_state import game_state
        
        actions = []
        # Number of hits = times used + 2
        num_hits = self.enemy.multi_stab_count + self._hits_base
        
        for _ in range(num_hits):
            damage = self.enemy.calculate_damage(self.base_damage)
            actions.append(AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        return actions


class BigStab(Intention):
    """Deals 21 damage."""
    
    def __init__(self, enemy: "BookOfStabbing"):
        super().__init__("Big Stab", enemy)
        self.base_damage = 21
    
    def execute(self) -> List:
        """Execute big stab attack."""
        from engine.game_state import game_state
        
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]
