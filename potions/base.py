import random
from typing import List, Optional
from actions.base import Action
from entities.creature import Creature
from localization import Localizable
from utils.types import RarityType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"
    can_be_used_actively = True  # Default: can be used actively, override if passive only

    def __init__(self):
        self._amount= 0
    
    @property
    def amount(self) -> int:
        """If player has relic: Sacred Bark, potion effects are doubled"""
        from engine.game_state import game_state
        if game_state.player and any(relic.idstr == "SacredBark" for relic in game_state.player.relics):
            return self._amount * 2
        return self._amount

    def on_use(self, target: Creature) -> List[Action]:
        """Base use method to be overridden by specific potions"""
        return []
    
    def info(self):
        """
        获取药水的完整信息显示
        
        返回格式：
        PotionName
        Description text
        """
        result = self.local("name") + f"\nRarity: {self.rarity.name.title()}"
        if hasattr(self, 'category') and self.category:
            result += f"\nCategory: {self.category}"
        result += "\n" + self.local("description")
        return result
