# Module: Orb
def get_game_state():
    from engine.game_state import game_state
    return game_state

def get_player():
    from player.player import Player
    return Player
from utils.types import TargetType
from localization import Localizable

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
