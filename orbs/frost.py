
from typing import List
from actions.base import Action, LambdaAction
from actions.combat import GainBlockAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.types import TargetType
from utils.dynamic_values import resolve_orb_value

class FrostOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_LOWEST_HP
    
    def __init__(self):
        self.passive_block = 2
        self.evoke_block = 5

    def on_passive(self) -> List[Action]:
        return [GainBlockAction(
            block=resolve_orb_value(self.passive_block),
            target=resolve_target(self.target_type)
        )]

    def on_evoke(self) -> List[Action]:
        return [GainBlockAction(
            block=resolve_orb_value(self.evoke_block),
            target=resolve_target(self.target_type)
        )]