import random
from typing import List, Optional
from actions.base import Action
from entities.creature import Creature
from localization import Localizable, t
from utils.types import RarityType, TargetType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"
    can_be_used_actively = True  # Default: can be used actively, override if passive only
    target_type = TargetType.SELF  # Default: targets the player

    def __init__(self):
        self._amount = 0
    
    @property
    def amount(self) -> int:
        """If player has relic: Sacred Bark, potion effects are doubled"""
        from engine.game_state import game_state
        if game_state.player and any(relic.idstr == "SacredBark" for relic in game_state.player.relics):
            return self._amount * 2
        return self._amount

    def on_use(self, targets: List[Creature]) -> List[Action]:
        """Base use method to be overridden by specific potions.
        
        Args:
            targets: List of resolved targets (single or multiple based on target_type)
        
        Returns:
            List of actions to execute
        """
        return []
    
    def info(self):
        """
        获取药水的完整信息显示
        
        返回格式：
        PotionName
        Description text
        """
        result = self.local("name") + f"\n{t('ui.rarity_label', 'Rarity: {rarity}', rarity=self.rarity.name.title())}"
        if hasattr(self, 'category') and self.category:
            result += f"\n{t('ui.category_label', 'Category: {category}', category=self.category)}"
        result += "\n" + self._get_dynamic_description()
        return result
    
    def _get_dynamic_description(self):
        """
        获取药水描述并动态替换变量
        
        Returns:
            替换变量后的描述文本
        """
        # 检查是否有描述
        if not self.has_local("description"):
            from localization import LocalStr
            return LocalStr(key="")
        
        # 构建变量字典
        variables = {}
        
        # 基础变量 - amount, damage, block, energy 等
        if hasattr(self, 'amount'):
            variables['amount'] = self.amount
        if hasattr(self, '_amount'):
            variables['damage'] = self.amount  # 爆炸药水等使用 amount 作为伤害
            variables['block'] = self.amount  # 格挡药水
            variables['energy'] = self.amount  # 能量药水
        
        # 特殊变量
        if hasattr(self, '__class__'):
            class_name = self.__class__.__name__
            
            # 爆炸药水 - 使用 damage 变量
            if class_name == "ExplosivePotion":
                variables['damage'] = self.amount
            
            # 格挡药水 - 使用 block 变量
            elif class_name == "BlockPotion":
                variables['block'] = self.amount
            
            # 能量药水 - 使用 energy 变量
            elif class_name == "EnergyPotion":
                variables['energy'] = self.amount
            
            # 抽牌药水 - 使用 amount 变量表示抽牌数
            elif class_name == "SwiftPotion":
                variables['amount'] = self.amount
            
            # 恐惧药水 - 使用 amount 和 duration 变量
            elif class_name == "FearPotion":
                variables['amount'] = self.amount
                variables['duration'] = self.amount
            
            # 火焰药水 - 使用 damage 变量
            elif class_name == "FirePotion":
                variables['damage'] = self.amount
            
            # 力量药水 - 使用 amount 变量
            elif class_name == "StrengthPotion":
                variables['amount'] = self.amount
            
            # 敏捷药水 - 使用 amount 变量
            elif class_name == "DexterityPotion":
                variables['amount'] = self.amount
            
            # 赌徒酿造 - 需要特殊处理，因为这个药水让玩家选择弃牌
            elif class_name == "GamblersBrew":
                # 赌徒酿造的描述不需要动态值
                pass
            
            # 邪教徒药水 - 使用 amount 变量
            elif class_name == "CultistPotion":
                variables['amount'] = self.amount
        
        # 返回带有格式化变量的 LocalStr 对象
        return self.local("description", **variables)