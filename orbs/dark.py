
from typing import List
from actions.base import Action, LambdaAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.types import TargetType
from utils.dynamic_values import resolve_orb_value, resolve_orb_damage

class DarkOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_LOWEST_HP
    base_charge = 6
    
    def __init__(self):
        self.charge = self.base_charge

    def on_passive(self) -> List[Action]:
        """
        Passive effect: increase charge by base charge value (6, modified by powers)

        Returns:
            None: No actions needed (just modifies charge value)
        """
        return [LambdaAction(func=lambda: setattr(self, "charge", self.charge + resolve_orb_value(self.base_charge)))]

    def on_evoke(self) -> List[Action]:
        """Evoke effect: deal magic damage equal to charge

        Returns:
            list: List of actions to execute
        """
        from actions.combat import DealDamageAction

        target = resolve_target(self.target_type)
        if target is None:
            return []  # No target available
        return [DealDamageAction(
            damage=resolve_orb_damage(self.charge, target),
            target=target,
            damage_type="magic"
        )]
