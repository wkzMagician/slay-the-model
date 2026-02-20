"""
Plated Armor power for combat effects.
Gain Block at end of turn; unblocked damage reduces stacks.
"""
from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from powers.base import Power
from utils.registry import register

@register("power")
class PlatedArmorPower(Power):
    """Gain Block at end of turn; unblocked damage reduces stacks."""
    
    name = "Plated Armor"
    description = "Gain Block at end of turn; unblocked damage reduces stacks."
    stackable = True
    amount_equals_duration = False
    is_buff = True  # Beneficial effect - provides block
    
    def __init__(self, amount: int = 4, duration: int = 0, owner=None):
        """
        Args:
            amount: Block to gain each turn (default 4)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_turn_end(self) -> List[Action]:
        from engine.game_state import game_state
        return super().on_turn_end() + [GainBlockAction(block=self.amount, target=game_state.player)]
    
    def on_damage_taken(self, damage: int, source: GainBlockAction = None, card: GainBlockAction = None, player: GainBlockAction = None, damage_type: str = "direct") -> List[Action]:
        if damage_type == "attack":
            self.amount -= 1
