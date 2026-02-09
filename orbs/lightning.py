
from typing import List
from actions.base import Action, LambdaAction
from actions.combat import DealDamageAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.types import TargetType
from utils.dynamic_values import resolve_orb_value

class LightningOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_RANDOM
    
    def __init__(self):
        self.passive_damage = 3
        self.evoke_damage = 8

    def on_passive(self) -> List[Action]:
        return [DealDamageAction(
            name="Lightning Orb",
            damage=resolve_orb_value(self.passive_damage),
            target=resolve_target(self.target_type),
            damage_type="magic"
        )]

    def on_evoke(self) -> List[Action]:
        return [DealDamageAction(
            name="Lightning Orb",
            damage=resolve_orb_value(self.evoke_damage),
            target=resolve_target(self.target_type),
            damage_type="magic"
        )]