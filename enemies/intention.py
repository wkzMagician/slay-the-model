"""Enemy intention system - defines what an enemy plans to do."""

from typing import List, TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from localization import Localizable, BaseLocalStr

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class Intention(ABC, Localizable):
    """Base class for enemy intentions.
    
    Each intention defines what an enemy plans to do and returns a list of Actions
    to execute when triggered.
    """
    
    # 本地化 - intentions are now nested under owner enemy
    localization_prefix = "enemies"
    localizable_fields = ("name", "description")
    
    def __init__(self, name: str, enemy: 'Enemy'):
        self.name = name
        self.enemy = enemy
        
        # 基础数值（子类在__init__中设置）
        self.base_damage = 0
        self.base_block = 0
        self.base_strength_gain = 0
        self.base_heal = 0
        self.base_amount = 0  # Generic amount for status effects
    
    @abstractmethod
    def execute(self) -> List['Action']:
        """Execute this intention and return list of actions to perform.

        Returns:
            List of Action objects to queue for execution
        """
        pass
    
    def _get_localized_key(self, field: str) -> str:
        """构建字段对应的本地化 key。
        
        Keys are structured as: enemies.{EnemyClass}.intentions.{intention_name}.{field}
        e.g., enemies.Cultist.intentions.ritual.name
        """
        # Get intention name from __dict__ to avoid property recursion
        intention_name = self.__dict__.get('name', 'unknown')
        # Get owner's class name (e.g., "Cultist")
        owner_class = self.enemy.__class__.__name__
        return f"{self.localization_prefix}.{owner_class}.intentions.{intention_name}.{field}"
    
    @property
    def description(self) -> 'BaseLocalStr':
        """获取意图描述（动态替换{damage}等变量）"""    
        # 动态替换变量
        variables = {}
        
        # 伤害值
        if self.base_damage > 0:
            from utils.dynamic_values import resolve_potential_damage
            from engine.game_state import game_state
            player = game_state.player
            variables['damage'] = resolve_potential_damage(self.base_damage, self.enemy, player)
        
        # 护盾值
        if self.base_block > 0:
            variables['block'] = self.base_block
        
        # 力量
        if self.base_strength_gain > 0:
            variables['strength_gain'] = self.base_strength_gain
        
        # 治疗值
        if self.base_heal > 0:
            variables['heal'] = self.base_heal
        
        # 通用数量（支持多种命名方式：base_amount, weak_stacks, vulnerable_stacks, frail_stacks）
        amount = self._get_amount()
        if amount > 0:
            variables['amount'] = amount
        
        # 卡牌数量 (用于 Corrosive Spit 等意图)
        if hasattr(self, 'base_cards') and self.base_cards > 0:
            variables['cards'] = self.base_cards
        
        # 攻击次数 (多次攻击才显示)
        hits = self._get_hits()
        if hits > 1:
            variables['hits'] = hits
        
        # 返回带变量的LocalStr对象
        return self.local("description", **variables)
    
    def _get_amount(self) -> int:
        """获取通用数量（支持多种命名方式）。
        
        优先级：base_amount > weak_stacks > vulnerable_stacks > frail_stacks
        """
        candidates = [
            'base_amount',
            'weak_stacks',
            'vulnerable_stacks',
            'frail_stacks',
        ]
        
        for attr in candidates:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, int) and value > 0:
                    return value
        
        return 0
    
    def _get_hits(self) -> int:
        """获取攻击次数（支持多种命名方式）。"""
        candidates = [
            'hits',
            'base_hits',
            'base_times',
            '_hits',
        ]
        
        for attr in candidates:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, int) and value > 0:
                    return value
        
        return 0
