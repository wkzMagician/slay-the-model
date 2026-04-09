"""
Plated Armor power for combat effects.
Gain Block at end of turn; unblocked damage reduces stacks.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class PlatedArmorPower(Power):
    """Gain Block at end of turn; unblocked damage reduces stacks."""
    
    name = "Plated Armor"
    description = "Gain Block at end of turn; unblocked damage reduces stacks."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - provides block
    
    def __init__(self, amount: int = 4, duration: int = -1, owner=None):
        """
        Args:
            amount: Block to gain each turn (default 4)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_turn_end(self):
        # Gain Block equal to stacks for the owner (enemy or player)
        super().on_turn_end()
        from engine.game_state import game_state
        add_actions([GainBlockAction(block=self.amount, target=self.owner)])
        return
    def on_physical_attack_taken(
        self,
        damage: int,
        source=None,
        card=None,
        player=None,
        damage_type: str = "physical",
    ):
        self.amount -= 1
        if self.amount <= 0 and self.owner is not None:
            self.owner.remove_power(self.name)
        return
