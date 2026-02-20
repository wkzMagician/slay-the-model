"""Taskmaster intentions - Act 2 Elite enemy."""

from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, ApplyPowerAction
from enemies.intention import Intention
from powers.base import PowerType

if TYPE_CHECKING:
    from enemies.taskmaster import Taskmaster


class ScouringWhip(Intention):
    """Deals 7 damage. Adds a Wound to discard pile. Gains 1 Strength (Asc 3+)."""
    
    def __init__(self, enemy: "Taskmaster"):
        super().__init__("Scouring Whip", enemy)
        self.base_damage = 7
    
    def execute(self) -> List:
        """Execute scouring whip attack."""
        from engine.game_state import game_state
        from cards.status_cards import Wound
        
        actions = []
        
        # Deal damage
        damage = self.enemy.calculate_damage(self.base_damage)
        actions.append(AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        ))
        
        # Add wound to player's discard pile
        wound = Wound()
        game_state.player.discard_pile.append(wound)
        
        # Asc 3+: Gain 1 Strength
        if game_state.ascension >= 3:
            actions.append(ApplyPowerAction(
                power=PowerType.STRENGTH,
                target=self.enemy,
                amount=1,
                duration=-1
            ))
        
        return actions
