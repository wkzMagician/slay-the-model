# Module: Orb
def get_game_state():
    from engine.game_state import game_state
    return game_state

def get_player():
    from player.player import Player
    return Player
from typing import List
from actions.base import Action
from utils.types import TargetType
from localization import Localizable

class Orb(Localizable):
    localization_prefix = "orbs"
    passive_timing = "turn_end"
    target_type = TargetType.SELF
    
    def __init__(self):
        pass

    def on_passive(self) -> List[Action]:
        """Return list of actions for passive effect

        Returns:
            list: List of actions to execute, or None
        """
        raise NotImplementedError

    def on_evoke(self) -> List[Action]:
        """Return list of actions for evoke effect

        Returns:
            list: List of actions to execute, or None
        """
        raise NotImplementedError
