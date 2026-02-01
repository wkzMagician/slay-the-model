import random
from typing import List
from actions.base import Action
from engine.game_state import game_state
from entities.creature import Creature
from utils.localizable import Localizable

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = "Common"
    category = "Global"
    amount = None

    def __init__(self):
        pass

    def on_use(self, target: Creature) -> List[Action]:
        """Base use method to be overridden by specific potions"""
        return []