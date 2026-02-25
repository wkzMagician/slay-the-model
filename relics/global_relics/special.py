"""
Special Relics
Special key items for the game.
"""
from typing import List
from actions.base import Action
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register

@register("relic")
class RedKey(Relic):
    """You need to obtain Red, Green and Blue Key. Why? Find out yourself!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SPECIAL

    # This is a quest item with no direct effect
    # Implemented as a passive effect description

@register("relic")
class BlueKey(Relic):
    """You need to obtain Red, Green and Blue Key. Why? Find out yourself!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SPECIAL

    # This is a quest item with no direct effect
    # Implemented as a passive effect description

@register("relic")
class GreenKey(Relic):
    """You need to obtain Red, Green and Blue Key. Why? Find out yourself!"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SPECIAL

    # This is a quest item with no direct effect
    # Implemented as a passive effect description

@register("relic")
class NeowsLament(Relic):
    """Neow's Lament - A special relic."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SPECIAL
        self.stacks = 3
    
    # This relic provides benefits when certain conditions are met
