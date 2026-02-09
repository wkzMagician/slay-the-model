
from typing import List
from actions.base import Action, LambdaAction
from actions.combat import GainEnergyAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.types import TargetType
from utils.dynamic_values import resolve_orb_value

class PlasmaOrb(Orb):
    passive_timing = "turn_start"
    target_type = TargetType.ENEMY_LOWEST_HP
    
    def __init__(self):
        self.passive_energy_gain = 1
        self.evoke_energy_gain = 2

    def on_passive(self) -> List[Action]:
        return [GainEnergyAction(energy=self.passive_energy_gain)]

    def on_evoke(self) -> List[Action]:
        return [GainEnergyAction(energy=self.evoke_energy_gain)]