import random
from typing import List
from actions.base import Action
from entities.creature import Creature
from localization import Localizable
from utils.types import RarityType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"

    def __init__(self):
        # Subclasses should set self._amount in their __init__
        # Default to None if not set by subclass
        if not hasattr(self, '_amount'):
            self._amount = None
    
    @property
    def amount(self):
        """If player has relic: Sacred Bark, potion effects are doubled"""
        from engine.game_state import game_state
        if game_state.player and any(relic.idstr == "SacredBark" for relic in game_state.player.relics):
            return self._amount * 2 if self._amount is not None else None
        return self._amount

    def on_use(self, target: Creature) -> List[Action]:
        """Base use method to be overridden by specific potions"""
        return []