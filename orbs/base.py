from engine.game_state import game_state
from player.player import Player
from utils.types import TargetType
from utils.localizable import Localizable

class Orb(Localizable):
    localization_prefix = "orbs"
    passive_timing = "turn_end"
    target_type = TargetType.SELF
    
    def __init__(self):
        pass

    def passive(self):
        raise NotImplementedError

    def evoke(self):
        raise NotImplementedError