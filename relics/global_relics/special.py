"""
Special Relics
Special key items for game.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action
from actions.display import DisplayTextAction
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
        
    def on_combat_start(self, floor: int):
        """在前三场战斗中设置所有敌人 HP=1"""
        from engine.game_state import game_state
        
        # 检查是否在前三场战斗中
        if self.stacks > 0:
            actions = []
            
            # 设置所有敌人的 HP 和最大 HP 为 1
            for enemy in self.combat_enemies():
                if hasattr(enemy, 'hp'):
                    enemy.hp = 1
                    
            # 添加显示消息
            actions.append(DisplayTextAction(
                text_key="relics.neows_lament.effect"
            ))
            
            self.stacks -= 1
            
            from engine.game_state import game_state
            
            add_actions(actions)
            
            return
        return
    # This relic provides benefits when certain conditions are met
