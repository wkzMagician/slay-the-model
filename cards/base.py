"""
Card base class - class-driven card system
"""
from entities.creature import Creature
from actions.combat import (
    DealDamageAction,
    GainBlockAction,
    HealAction,
    DrawCardsAction,
    GainEnergyAction,
)
from actions.card import ExhaustCardAction
from cards.description_parser import description_parser
from engine.game_state import game_state

COST_X = -1
COST_UNPLAYABLE = -2


class Card:
    """Advanced card class with dynamic values and multiple triggers"""

    # * card attributes
    card_type = "Attack"  # Attack, Skill, Power, Status, Curse
    rarity = "Starter"  # Starter, Common, Uncommon, Rare
    color = "Red"  # Red, Green, Blue, Purple, Colorless
    description_template = ""
    upgrade_description_template = None

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

    def __init__(self, card_name=None):
        # ***** Basic card attributes
        # todo: card registry
        from cards.registry import _namespace_from_module
        self.card_id = getattr(self, "card_id", None)
        if not self.card_id:
            namespace = _namespace_from_module(self.__class__.__module__)
            if namespace:
                self.card_id = f"{namespace}.{self.name}"
        self.base_name = self.name
        if card_name:
            self.name = card_name
        else:
            self.name = self.base_name
        from localization import t
        key_name = self.card_id or self.base_name
        self.name = t(f"cards.{key_name}.name", default=self.name)
        if self.name == (self.card_id or self.base_name):
            self.name = t(f"cards.{self.base_name}.name", default=self.name)
        self.display_name_base = self.name
        self.description_template = self._resolve_description_template(
            key_name,
            self.description_template,
        )
        self.upgrade_description_template = self._resolve_description_template(
            key_name,
            self.upgrade_description_template,
            suffix="description_upgraded",
        )
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
        self.description = self._generate_description()
 
    def __str__(self):
        cost = self.get_temp_value("cost")
        if cost == COST_X:
            cost_str = "X"
        elif cost == COST_UNPLAYABLE:
            cost_str = "-"
        else:
            cost_str = str(cost)
        return f"{self.name} ({cost_str}) - {self.card_type}"
    
    def __repr__(self):
        return self.__str__()
    
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
        if target_type:
            return target_type
        card_type = str(getattr(self, "type", "") or "").lower()
        if card_type in ("skill", "power"):
            return "self"
        if card_type == "attack":
            # 单体/群体，默认为单体
            return "select"
        return target_type

    # * * * value 相关
    
    def get_temp_value(self, key):
        """Get current value considering all modifiers"""
        return self.temp_values[key]
    
    def modify_combat_value(self, key, value):
        """Modify a card value (for buffs/debuffs)"""
        self.combat_values[key] = value
        self.recalculate_temp_value(key, value)
        
    def recalculate_temp_value(self, key, value):
        """Modify a card value (for buffs/debuffs)"""
        # todo: 调用util里的函数
        # Regenerate description with new values
        self.description = self._generate_description()
    
    def recalculate_all_temp_values(self):
        """Modify a card value (for buffs/debuffs)"""
        for key, value in self.base_values.items():
            self.recalculate_temp_value(key, value)     

    # * * * desctiption 相关
    def _generate_description(self):
        """Generate description with dynamic values"""
        return description_parser.parse(self.description_template, self)

    def _resolve_description_template(self, key_name, fallback, suffix="description"):
        from localization import t
        key = f"cards.{key_name}.{suffix}"
        value = t(key, default=key)
        if value == key:
            key = f"cards.{self.base_name}.{suffix}"
            value = t(key, default=key)
        if value == key:
            return fallback
        return value

    # * * * actions 相关

    def on_play(self, target:Creature|None=None):
        """卡牌被打出时触发，默认返回 Action 列表。"""
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

        if not ignore_energy and game_state.player and hasattr(game_state.player, 'energy'):
            cost = self.get_temp_value('cost')
            if cost == COST_X:
                if game_state.player.energy <= 0:
                    return False, "Not enough energy."
            elif game_state.player.energy < cost:
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
            self.name = f"{self.display_name_base}+"
        else:
            # For cards that can be upgraded multiple times (like Searing Blow)
            self.name = f"{self.display_name_base}+{self.upgrade_level}"

        # Apply upgrade effects
        self.apply_upgrade()

        if self.upgrade_description_template:
            self.description_template = self.upgrade_description_template
        # Regenerate description with new values
        self.description = self._generate_description()

        from localization import t
        print(t(
            "ui.card_upgraded",
            default=f"Upgraded {self.name} (level {self.upgrade_level})",
            card=self.name,
            level=self.upgrade_level,
        ))
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
    