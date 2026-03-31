"""
Card base class - class-driven card system with namespace support
"""
from engine.runtime_api import add_action, add_actions
from typing import Any, Dict, List, Optional
from actions.base import Action, LambdaAction
from actions.combat import AttackAction
from entities.creature import Creature
from engine.messages import (
    CardDiscardedMessage,
    CardDrawnMessage,
    CardPlayedMessage,
    DamageResolvedMessage,
    HpLostMessage,
    PlayerTurnEndedMessage,
)
from engine.subscriptions import MessagePriority, subscribe
# 延迟导入以避免循环导入
def get_game_state():
    from engine.game_state import game_state
    return game_state
from utils.types import CardType, TargetType, RarityType
from cards.namespaces import get_color_for_namespace, namespace_from_module
from localization import Localizable
from localization import BaseLocalStr, LocalStr, ConcatLocalStr, localize_card_type, localize_rarity, t

COST_X = -1
COST_UNPLAYABLE = -2

class RawLocalStr(BaseLocalStr):
    """包装静态字符串的LocalStr基类实现"""
    def __init__(self, text: str):
        self.text = text
    
    def resolve(self) -> str:
        return self.text


class Card(Localizable):
    """Advanced card class with dynamic values and multiple triggers"""

    # * card attributes
    card_type = CardType.ATTACK
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

    upgrade_cost: Optional[int] = None
    upgrade_damage: Optional[int] = None
    upgrade_block: Optional[int] = None
    upgrade_heal: Optional[int] = None
    upgrade_draw: Optional[int] = None
    upgrade_energy_gain: Optional[int] = None
    upgrade_attack_times: Optional[int] = None
    upgrade_magic: Optional[Dict[str, Any]] = None
    
    upgrade_exhaust: Optional[bool] = None
    upgrade_ethereal: Optional[bool] = None
    upgrade_retain: Optional[bool] = None
    upgrade_innate: Optional[bool] = None
    
    # * card behavior
    upgradeable = True
    upgrade_limit = 1
    
    # * whether the card can be removed from deck
    removable = True

    # * card triggers
    target_type = None
    
    localization_prefix = "cards"
    localizable_fields = ("name", "description", "upgrade_description", "combat_description", "upgrade_combat_description")

    def __init__(self, **kwargs):
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

        # 私有化数值字段（战斗数值）
        self._cost = self.base_cost
        self._damage = self.base_damage
        self._block = self.base_block
        self._heal = self.base_heal
        self._draw = self.base_draw
        self._energy_gain = self.base_energy_gain
        self._attack_times = self.base_attack_times
        self._magic = dict(self.base_magic or {})
        self._exhaust = self.base_exhaust
        self._ethereal = self.base_ethereal
        self._retain = self.base_retain
        self._innate = self.base_innate

        # Bottled status - whether this card is bottled by a relic
        self.bottled = False

        # Computed properties
        self.target_type = self._resolve_target()
        self.retain_this_turn = False
        
        # temporary cost until end of turn (e.g. from Corruption/Bullet Time)
        self.cost_until_end_of_turn: Optional[int] = None
        self.cost_until_played: Optional[int] = None
        self._x_cost_energy = 0
        
        # Handle optional kwargs for testing
        if kwargs.get("name"):
            self._name = kwargs["name"]
        if kwargs.get("card_type"):
            self.card_type = kwargs["card_type"]
        if kwargs.get("base_cost") is not None:
            self._base_cost = kwargs["base_cost"]
            self._cost = kwargs["base_cost"]
        if kwargs.get("base_damage") is not None:
            self._base_damage = kwargs["base_damage"]
            self._damage = kwargs["base_damage"]
        if kwargs.get("upgrade_level") is not None:
            self.upgrade_level = kwargs["upgrade_level"]
            # Re-resolve target_type after upgrade_level is set
            self.target_type = self._resolve_target()

    @property
    def idstr(self) -> str:
        """Card ID with namespace, e.g. 'Base.Strike'"""
        return f"{self.namespace}.{self.__class__.__name__}"
 
    # ============ 数值属性访问器 ============
    
    @property
    def cost(self) -> int:
        """获取消耗能量"""
        if self._cost == COST_X:
            from engine.game_state import game_state
            return game_state.player.energy
        if self.cost_until_end_of_turn is not None:
            return self.cost_until_end_of_turn
        if self.cost_until_played is not None:
            return self.cost_until_played
        return self._cost
    
    @cost.setter
    def cost(self, value: int):
        """设置消耗能量"""
        if self._cost != COST_UNPLAYABLE or self._cost != COST_X:
            self._cost = value
    
    @property
    def damage(self) -> int:
        """获取基础伤害"""
        return self._damage
    
    @property
    def block(self) -> int:
        """获取基础格挡"""
        return self._block
    
    @property
    def heal(self) -> int:
        """获取基础治疗"""
        return self._heal
    
    @property
    def draw(self) -> int:
        """获取抽牌数"""
        return self._draw
    
    @property
    def energy_gain(self) -> int:
        """获取能量获得"""
        return self._energy_gain
    
    @property
    def attack_times(self) -> int:
        """获取攻击次数"""
        return self._attack_times

    def get_effective_x(self) -> int:
        """Get the resolved X value for this play, including Chemical X."""
        from engine.game_state import game_state

        x_value = int(getattr(self, "_x_cost_energy", 0) or 0)
        player = getattr(game_state, "player", None)
        if player is None:
            return x_value

        has_chemical_x = any(
            getattr(relic, "idstr", None) == "ChemicalX"
            for relic in getattr(player, "relics", [])
        )
        return x_value + 2 if has_chemical_x else x_value
    
    @property
    def exhaust(self) -> bool:
        """是否消耗"""
        return self._exhaust
    
    @property
    def ethereal(self) -> bool:
        """是否虚幻"""
        return self._ethereal
    
    @property
    def retain(self) -> bool:
        """是否保留"""
        return self._retain
    
    @property
    def innate(self) -> bool:
        """是否固有"""
        return self._innate

    @property
    def retain_for_this_turn(self) -> bool:
        return self.retain_this_turn

    @retain_for_this_turn.setter
    def retain_for_this_turn(self, value: bool):
        self.retain_this_turn = bool(value)

    
    # ============ 动态值获取 ============
    
    def get_value(self, value_type: str, source: Optional[Creature] = None) -> int:
        """
        获取动态计算的值
        
        Args:
            value_type: 值类型 ('damage', 'block', 'heal', 'draw', 'energy', 'attack_times')
            source: 来源生物
        
        Returns:
            动态计算后的值
        """
        from utils.dynamic_values import resolve_card_value
        return resolve_card_value(self, value_type)
    
    def get_magic_value(self, magic_key: str, default: Any = 0) -> Any:
        """获取magic字典中的值"""
        from utils.dynamic_values import get_magic_value
        return get_magic_value(self, magic_key, default)
    
    # ============ 描述生成 ============
    
    @property
    def description(self) -> BaseLocalStr:
        """获取基础描述（卡牌列表/商店显示）"""
        return self._get_description("description")
    
    @property
    def combat_description(self) -> BaseLocalStr:
        """获取战斗描述（战斗中显示，包含动态值）"""
        return self._get_description("combat_description", fallback="description")
    
    def _get_description(self, desc_key: str, fallback: Optional[str] = None) -> BaseLocalStr:
        """
        获取描述模板并动态替换变量
        
        Args:
            desc_key: 描述键名
            fallback: 如果没有该描述，使用的回退键名
        
        Returns:
            替换变量后的描述文本
        """
        # 特殊处理：如果是战斗描述且已升级，检查是否有升级后的战斗描述
        original_desc_key = desc_key
        if desc_key == "combat_description" and self.upgrade_level > 0:
            if self.has_local("upgrade_combat_description"):
                desc_key = "upgrade_combat_description"
        
        # 检查是否有该描述
        if not self.has_local(desc_key):
            if fallback:
                desc_key = fallback
            else:
                # Return empty LocalStr instead of raw BaseLocalStr
                return LocalStr(key="")
        
        # 构建变量字典
        from utils.dynamic_values import resolve_card_value
        variables = {}
        is_combat_description = original_desc_key == "combat_description"
        
        # 基础变量
        value_types = ['damage', 'block', 'heal', 'draw', 'energy_gain', 'attack_times']
        for vt in value_types:
            if is_combat_description:
                variables[vt] = resolve_card_value(self, vt)
            else:
                variables[vt] = getattr(self, vt)
        
        # magic变量 - create nested dict for format() to access via {magic.key}
        if hasattr(self, '_magic'):
            magic_dict = type('MagicDict', (), {k: v for k, v in self._magic.items()})()
            variables['magic'] = magic_dict
        
        # 返回带有格式化变量的 LocalStr 对象
        return self.local(desc_key, **variables)
        
    
    def info(self) -> BaseLocalStr:
        """
        获取战斗中的完整信息显示
        
        返回格式：
        CardName (Cost: X, Type: Attack, Rarity: Common)
        Description text {damage} {block}
        """
        from utils.dynamic_values import resolve_card_value
        
        cost = resolve_card_value(self, 'cost')
        cost_str = str(cost)
        if self._cost == COST_X:
            cost_str = "X"
        elif self._cost == COST_UNPLAYABLE:
            cost_str = "#"
        
        # 获取战斗描述（如果有的话）
        if self.has_local("combat_description"):
            desc = self._get_description("combat_description")
        else:
            desc = self.description
        
        # 使用字符串拼接，避免嵌套的 t() 调用
        cost_label = t("ui.cost_label", default="Cost")
        type_label = t("ui.type_label", default="Type: {type}", type=localize_card_type(self.card_type))
        rarity_label = t("ui.rarity_label", default="Rarity: {rarity}", rarity=localize_rarity(self.rarity))

        info_text = f"{self.display_name} ({cost_label}: {cost_str}, {type_label}, {rarity_label})\n{desc}"
        return RawLocalStr(info_text)
    

    def _resolve_target(self):
        # Check for upgrade-based target_type first
        if self.upgrade_level > 0:
            upgrade_target_type = getattr(self.__class__, "upgrade_target_type", None)
            if upgrade_target_type and isinstance(upgrade_target_type, TargetType):
                return upgrade_target_type
        else:
            base_target_type = getattr(self.__class__, "base_target_type", None)
            if base_target_type and isinstance(base_target_type, TargetType):
                return base_target_type
        
        # Fall back to static target_type
        target_type = getattr(self, "target_type", None)
        if target_type and isinstance(target_type, TargetType):
            return target_type
        # Get card_type - handle both enum and string
        card_type_attr = getattr(self, "card_type", None)
        if card_type_attr is None:
            return None
        # If it's an enum, get its value; otherwise convert to string
        if hasattr(card_type_attr, 'value'):
            card_type = card_type_attr.value.lower()
        else:
            card_type = str(card_type_attr).lower()
        
        if card_type in ("skill", "power", "status", "curse"):
            return TargetType.SELF
        if card_type == "attack":
            # 单体/群体, 默认为单体
            return TargetType.ENEMY_SELECT
        return None


    # * * * actions 相关

    def on_play(self, targets: List[Creature] = []):
        """卡牌被打出时触发，返回 Action 列表"""
        # Extract first target for compatibility
        try:
            from actions.combat import (
                GainBlockAction,
                HealAction,
                GainEnergyAction,
                LoseHPAction,
            )
            from actions.card import ExhaustCardAction, DrawCardsAction
            
            from utils.dynamic_values import resolve_card_value
            from engine.game_state import game_state
            source = game_state.player
            
            actions = []
            
            # 格挡 (block always goes to player)
            if self.block > 0:
                block_value = resolve_card_value(self, 'block')
                actions.append(GainBlockAction(block=lambda: block_value, target=source))
            
            # 伤害
            if self.damage > 0:
                hits = max(1, resolve_card_value(self, 'attack_times'))
                for target in targets:
                    for _ in range(hits):
                        # Use unified damage pipeline via AttackAction so Strength/Weak/Vulnerable etc. are applied correctly.
                        action = AttackAction(
                            damage=self.damage,
                            target=target,
                            source=source,
                            damage_type="attack",
                            card=self,
                        )
                        actions.append(action)
            
            # 治疗
            if self.heal > 0:
                heal_value = resolve_card_value(self, 'heal')
                actions.append(HealAction(amount=heal_value))
            elif self.heal < 0:
                hp_loss = abs(resolve_card_value(self, 'heal'))
                actions.append(LoseHPAction(amount=hp_loss))
            
            # 抽牌
            if self.draw > 0:
                draw_value = resolve_card_value(self, 'draw')
                actions.append(DrawCardsAction(count=lambda: draw_value))
            
            # 能量
            if self.energy_gain > 0:
                energy_value = resolve_card_value(self, 'energy_gain')
                actions.append(GainEnergyAction(energy=lambda: energy_value))
            
            # 消耗
            if self.exhaust:
                actions.append(ExhaustCardAction(card=self, source_pile="hand"))
            
            add_actions(actions)
            return
        except ImportError:
            return

    @subscribe(CardDiscardedMessage, priority=MessagePriority.CARD)
    def on_discard(self):
        """卡牌被弃置时触发，默认返回 Action 列表。"""
        return

    @subscribe(CardDrawnMessage, priority=MessagePriority.CARD)
    def on_draw(self):
        """卡牌被抽到时触发，默认返回 Action 列表。"""
        return

    def on_exhaust(self):
        """卡牌被消耗（放逐）时触发，默认返回 Action 列表。"""
        return
    
    @subscribe(CardPlayedMessage, priority=MessagePriority.REACTION)
    def on_card_play(self, card, player, targets):
        """Called when another card is played while this card is active."""
        return

    def on_player_turn_start(self):
        """
        卡牌在回合开始时触发。
        默认：如果本回合费用覆写不为None，重置为None（只影响当前回合）
        """
        from engine.game_state import game_state
        add_action(LambdaAction(lambda: setattr(self, 'cost_until_end_of_turn', None)))
        return
    
    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.CARD)
    def on_player_turn_end(self):
        """卡牌在回合结束时触发，默认返回 Action 列表。"""
        return

    @subscribe(DamageResolvedMessage, priority=MessagePriority.REACTION)
    def on_damage_dealt(self, damage: int, target=None, card=None, damage_type: str = "direct"):
        """Called when this card deals damage."""
        return

    @subscribe(DamageResolvedMessage, priority=MessagePriority.REACTION)
    def on_damage_taken(self, damage: int, source=None, card=None, player=None, damage_type: str = "direct"):
        """Called when damage is resolved while this card is active."""
        return

    @subscribe(HpLostMessage, priority=MessagePriority.REACTION)
    def on_lose_hp(self, amount: int, source=None, card=None):
        """Called when HP loss is resolved while this card is active."""
        return

    @subscribe(DamageResolvedMessage, priority=MessagePriority.REACTION)
    def on_fatal(self, damage: int, target=None, card=None, damage_type: str = "direct"):
        """Called when this card delivers a killing blow."""
        return

    def can_play(self, ignore_energy=False) -> tuple[bool, Optional[str]]:
        """Check if this card can be played."""
        from engine.game_state import game_state
        from utils.types import CardType
        assert game_state.current_combat is not None
        combat_state = game_state.current_combat.combat_state
        if not combat_state.turn_enable_card_play:
            return False, "Normality restriction"
        
        # VelvetChoker restriction: cannot play more than 6 cards per turn
        if game_state.player:
            for relic in game_state.player.relics:
                if relic.__class__.__name__ == "VelvetChoker":
                    if combat_state.turn_cards_played >= 6:
                        return False, "Velvet Choker restriction (max 6 cards per turn)"
                    break
        
        cost = self.cost
        
        if cost == COST_UNPLAYABLE:
            if (
                self.card_type == CardType.STATUS
                and game_state.player
                and any(
                    getattr(relic, "idstr", None) == "MedicalKit"
                    for relic in game_state.player.relics
                )
            ):
                return True, None
            if (
                self.card_type == CardType.CURSE
                and game_state.player
                and any(
                    getattr(relic, "idstr", None) == "BlueCandle"
                    for relic in game_state.player.relics
                )
            ):
                return True, None
            return False, "Unplayable card."

        if not ignore_energy and game_state.player:
            if cost == COST_X:
                return True, None
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
            self.display_name = self.local("name") + "+"
        else:
            # For cards that can be upgraded multiple times (like Searing Blow)
            self.display_name = self.local("name") + f"+{self.upgrade_level}"

        # Apply upgrade effects
        self.apply_upgrade()
        
        # Check if there's an upgraded combat description
        if self.has_local("upgrade_combat_description"):
            # Store that we have upgraded combat description
            self._has_upgrade_combat_desc = True
        
        return True

    def apply_upgrade(self):
        """Apply upgrade effects to card values."""
        if self.upgrade_damage is not None:
            self._damage = self.upgrade_damage
        if self.upgrade_block is not None:
            self._block = self.upgrade_block
        if self.upgrade_heal is not None:
            self._heal = self.upgrade_heal
        if self.upgrade_draw is not None:
            self._draw = self.upgrade_draw
        if self.upgrade_energy_gain is not None:
            self._energy_gain = self.upgrade_energy_gain
        if self.upgrade_cost is not None:
            self._cost = self.upgrade_cost
        if self.upgrade_magic:
            for key, value in self.upgrade_magic.items():
                self._magic[key] = value
        if self.upgrade_attack_times is not None:
            self._attack_times = self.upgrade_attack_times
        if self.upgrade_retain is not None:
            self._retain = self.upgrade_retain
        if self.upgrade_exhaust is not None:
            self._exhaust = self.upgrade_exhaust
        if self.upgrade_ethereal is not None:
            self._ethereal = self.upgrade_ethereal
        if self.upgrade_innate is not None:
            self._innate = self.upgrade_innate

    def copy(self) -> "Card":
        """Create a copy of this card.
        
        Used when shuffling deck to create independent card instances
        for each combat.
        
        Returns:
            Card: A new Card instance that is a copy of this card.
        """
        import copy
        return copy.copy(self)
