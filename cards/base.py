"""
Card base class - class-driven card system with namespace support
"""
from typing import Any, List, Optional
from actions.base import Action
from entities.creature import Creature
# 延迟导入以避免循环导入
def get_game_state():
    from engine.game_state import game_state
    return game_state
from utils.types import TargetType, RarityType
from cards.namespaces import get_color_for_namespace, namespace_from_module
from localization import Localizable
from localization import BaseLocalStr, LocalStr

COST_X = -1
COST_UNPLAYABLE = -2


class Card(Localizable):
    """Advanced card class with dynamic values and multiple triggers"""

    # * card attributes
    card_type = "Attack"  # Attack, Skill, Power, Status, Curse
    rarity = RarityType.COMMON

    # * card values
    base_cost = 0
    base_damage = 0
    base_block = 0
    base_heal = 0
    base_draw = 0
    base_energy_gain = 0
    base_attack_times = 1
    base_magic = None
    
    base_exhaust = False
    base_ethereal = False
    base_retain = False
    base_innate = False

    upgrade_cost = None
    upgrade_damage = None
    upgrade_block = None
    upgrade_heal = None
    upgrade_draw = None
    upgrade_energy_gain = None
    upgrade_attack_times = None
    upgrade_magic = None
    
    upgrade_exhaust = None
    upgrade_ethereal = None
    upgrade_retain = None
    upgrade_innate = None
    
    # * card behavior
    upgradeable = True
    upgrade_limit = 1

    # * card triggers
    target_type = None
    
    localizable_fields = ("name", "description", "upgrade_description")

    def __init__(self):
        # ***** Basic card attributes with namespace support
        # Determine namespace from module path
        self.namespace = namespace_from_module(self.__class__.__module__)
        
        # Set color based on namespace
        self.color = get_color_for_namespace(self.namespace)
        
        # Get class name as base name
        self.display_name : BaseLocalStr = self.local("name")
        self.description_template : BaseLocalStr = self.local("description")
        
        # ************************

        # Upgrade info
        self.upgradeable = bool(getattr(self, "upgradeable", True))
        self.upgrade_limit = int(getattr(self, "upgrade_limit", 1))
        self.upgrade_level = 0  # Current upgrade level

        # Value system - base, combat, and temporary values
        self.base_values = self._extract_base_values() # 基础设定值
        self.combat_values = self.base_values.copy()  # 战斗中的基准值。例子：爪击
        self.temp_values = self.base_values.copy()    # 临时的值，受遗物和能力影响
        
        # ! 对于cost的special字段
        self.cost_for_trun = None

        # Computed properties
        self.target_type = self._resolve_target()
        self.update_description()
        
    @property
    def idstr(self) -> str:
        """Card ID with namespace, e.g. 'Base.Strike'"""
        return f"{self.namespace}.{self.__class__.__name__}"
 
    def __str__(self):
        """Display name for in-game use (without namespace)"""
        # todo
        pass
    
    def __repr__(self):
        """Debug representation with namespace"""
        # todo
        pass
    
    def _extract_base_values(self):
        """Extract base values from class attributes"""
        base_values = {
            'cost': self.base_cost,
            'damage': self.base_damage,
            'block': self.base_block,
            'heal': self.base_heal,
            'draw': self.base_draw,
            'energy_gain': self.base_energy_gain,
            'magic': dict(getattr(self, "base_magic", {}) or {}),
            'attack_times': int(getattr(self, "base_attack_times", 1)),
            'retain': bool(getattr(self, "retain", False)),
            'exhaust': bool(getattr(self, "exhaust", False)),
            'ethereal': bool(getattr(self, "ethereal", False)),
            'innate': bool(getattr(self, "innate", False)),
        }
        return base_values

    def _resolve_target(self):
        target_type = getattr(self, "target_type", None)
        if target_type and isinstance(target_type, TargetType):
            return target_type
        card_type = str(getattr(self, "type", "") or "").lower()
        if card_type in ("skill", "power"):
            return TargetType.SELF
        if card_type == "attack":
            # 单体/群体, 默认为单体
            return TargetType.ENEMY_SELECT
        return None

    def get_temp_value(self, key):
        """Get current value considering all modifiers"""
        return self.temp_values[key]
    
    def modify_combat_value(self, key, value):
        """Modify a card value (for buffs/debuffs)"""
        self.combat_values[key] = value
        self.recalculate_temp_value(key, value)
        
    def recalculate_temp_value(self, key, value):
        """Modify a card value (for buffs/debuffs)"""
        # todo: 调用util里的函数，更新self.temp_values
        # Regenerate description with new values
        self.update_description()
    
    def recalculate_all_temp_values(self):
        """Modify a card value (for buffs/debuffs)"""
        for key, value in self.base_values.items():
            self.recalculate_temp_value(key, value)

    def update_description(self):
        """Regenerate description based on current temp values"""
        self.description = self.local("description", **self.temp_values)

    # * * * actions 相关

    def on_play(self, target:Optional[Creature]=None) -> List[Action]:
        """卡牌被打出时触发，默认返回 Action 列表。"""
        # Import actions here to avoid circular imports
        try:
            # todo: Card Actions
            from actions.combat import (
                DealDamageAction,
                GainBlockAction,
                HealAction,
                DrawCardsAction,
                GainEnergyAction,
            )
            from actions.card import ExhaustCardAction
            
            actions = []
            if self.base_values.get('block', 0) > 0:
                actions.append(GainBlockAction(block=lambda: self.get_temp_value('block')))
            if self.base_values.get('damage', 0) > 0:
                hits = max(1, int(self.get_temp_value('attack_times')))
                for _ in range(hits):
                    action = DealDamageAction(
                        "deal_damage_action",
                        damage=lambda: self.get_temp_value('damage'),
                        target=target,
                        damage_type="direct",
                    )
                    action.card = self
                    actions.append(action)
            if self.base_values.get('heal', 0) > 0:
                actions.append(HealAction(heal=lambda: self.get_temp_value('heal')))
            if self.base_values.get('draw', 0) > 0:
                actions.append(DrawCardsAction(count=lambda: self.get_temp_value('draw')))
            if self.base_values.get('energy_gain', 0) > 0:
                actions.append(GainEnergyAction(energy=lambda: self.get_temp_value('energy_gain')))
            if self.base_values.get('exhaust', False):
                actions.append(ExhaustCardAction(card=self, source_pile="hand"))
            return actions
        except ImportError:
            # Return empty list if actions are not available
            return []

    def on_discard(self):
        """卡牌被弃置时触发，默认返回 Action 列表。"""
        return []

    def on_draw(self):
        """卡牌被抽到时触发，默认返回 Action 列表。"""
        return []

    def on_exhaust(self):
        """卡牌被消耗（放逐）时触发，默认返回 Action 列表。"""
        return []

    def can_play(self, ignore_energy=False):
        """Check if this card can be played."""
        if self.get_temp_value('cost') == COST_UNPLAYABLE:
            return False, "Unplayable card."

        if not ignore_energy and get_game_state().player and hasattr(get_game_state().player, 'energy'):
            cost = self.get_temp_value('cost')
            if cost == COST_X:
                if get_game_state().player.energy <= 0:
                    return False, "Not enough energy."
            elif get_game_state().player.energy < cost:
                return False, "Not enough energy."

        return True, None

    # * * * upgrade 相关

    def can_upgrade(self):
        """Check if this card can be upgraded"""
        return self.upgradeable and self.upgrade_level < self.upgrade_limit

    def upgrade(self):
        """Upgrade this card"""
        if not self.can_upgrade():
            return False

        self.upgrade_level += 1

        # Update name with upgrade level
        if self.upgrade_level == 1:
            self.display_name = self.local("name") + "+"
        else:
            # For cards that can be upgraded multiple times (like Searing Blow)
            self.display_name = self.local("name") + f"+{self.upgrade_level}"

        # Apply upgrade effects
        self.apply_upgrade()

        if self.has_local("upgrade_description"):
            self.description_template = self.local("upgrade_description")
        else:
            self.description_template = self.local("description")
        # Regenerate description with new values
        self.update_description()

        # todo：打印信息
        return True

    def apply_upgrade(self):
        """Apply upgrade effects to card values."""
        if self.upgrade_damage is not None:
            self.combat_values['damage'] += self.upgrade_damage - self.base_damage
            self.base_values['damage'] = self.upgrade_damage
        if self.upgrade_block is not None:
            self.combat_values['block'] += self.upgrade_block - self.base_block
            self.base_values['block'] = self.upgrade_block
        if self.upgrade_heal is not None:
            self.combat_values['heal'] += self.upgrade_heal - self.base_heal
            self.base_values['heal'] = self.upgrade_heal
        if self.upgrade_draw is not None:
            self.combat_values['draw'] += self.upgrade_draw - self.base_draw
            self.base_values['draw'] = self.upgrade_draw
        if self.upgrade_energy_gain is not None:
            self.combat_values['energy_gain'] += self.upgrade_energy_gain - self.base_energy_gain
            self.base_values['energy_gain'] = self.upgrade_energy_gain
        if self.upgrade_cost is not None:
            self.combat_values['cost'] += self.upgrade_cost - self.base_cost
            self.base_values['cost'] = self.upgrade_cost
        if self.upgrade_magic:
            self.combat_values['magic'] = self.upgrade_magic
            self.base_values['magic'] = self.upgrade_magic
        if self.upgrade_attack_times is not None:
            self.combat_values['attack_times'] += self.upgrade_attack_times - self.base_attack_times
            self.base_values['attack_times'] = self.upgrade_attack_times
        if self.upgrade_retain is not None:
            self.combat_values['retain'] = self.upgrade_retain
            self.base_values['retain'] = self.upgrade_retain
        if self.upgrade_exhaust is not None:
            self.combat_values['exhaust'] = self.upgrade_exhaust
            self.base_values['exhaust'] = self.upgrade_exhaust
        if self.upgrade_ethereal is not None:
            self.combat_values['ethereal'] = self.upgrade_ethereal
            self.base_values['ethereal'] = self.upgrade_ethereal
        if self.upgrade_innate is not None:
            self.combat_values['innate'] = self.upgrade_innate
            self.base_values['innate'] = self.upgrade_innate
            
        self.recalculate_all_temp_values()
