"""
Power base class for combat effects.
Powers modify creature stats, damage calculations, and combat flow.
"""
from enum import Enum, auto
from typing import List, Optional, Any
from actions.base import Action
from engine.messages import (
    AnyHpLostMessage,
    AttackPerformedMessage,
    BlockGainedMessage,
    CardExhaustedMessage,
    CardPlayedMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CombatEndedMessage,
    DamageDealtMessage,
    DirectHpLossMessage,
    HealedMessage,
    HpLostMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
    PlayerTurnPostDrawMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PowerAppliedMessage,
)
from engine.subscriptions import MessagePriority, subscribe
from localization import Localizable, LocalStr, has_translation, t
from utils.types import TargetType
from utils.damage_phase import DamagePhase


class StackType(Enum):
    """Defines how a power stacks when reapplied."""
    INTENSITY = auto()      # Stacks amount only (Strength, Dexterity, Thorns)
    DURATION = auto()       # Stacks duration only (Vulnerable, Weak, Frail)
    BOTH = auto()           # Stacks both amount AND duration (Poison, Regen)
    LINKED = auto()         # Amount and duration are synchronized
    PRESENCE = auto()       # Single instance only (Barricade)
    MULTI_INSTANCE = auto() # Creates new instance each time (The Bomb)


class Power(Localizable):
    """Base power class for temporary and permanent combat effects."""
    
    # Localization
    localization_prefix = "powers"
    localizable_fields = ("name", "description")
    
    # Power behavior
    stack_type: StackType = StackType.INTENSITY  # How this power stacks
    amount_equals_duration: bool = False  # Should amount be set to duration on apply?
    is_buff: bool = True  # True for beneficial effects, False for harmful effects
    
    # Damage modification phase
    # ADDITIVE: Applied first (e.g., Strength +3)
    # MULTIPLICATIVE: Applied second (e.g., Weak 0.75x)
    # CAPPING: Applied last (e.g., Intangible caps at 1)
    modify_phase: DamagePhase = DamagePhase.ADDITIVE
    
    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        """Initialize power with amount and duration.
        
        Args:
            amount: Effect magnitude
            duration: How long the power lasts
            owner: The creature that has this power
        """
        self._amount = amount
        self._duration = duration
        self.owner = owner
        self.stack_type = self.__class__.stack_type
        self.amount_equals_duration = self.__class__.amount_equals_duration
        self.is_buff = self.__class__.is_buff
        if not hasattr(self, "localization_key"):
            self.localization_key = f"{self.localization_prefix}.{self.__class__.__name__}"

    @staticmethod
    def _normalized_name_candidates(value: str) -> List[str]:
        """Generate common localization key variants for power names."""
        variants = []
        if not value:
            return variants
        stripped = value.strip()
        compact = stripped.replace(" ", "")
        snake = stripped.replace(" ", "_")
        lower_snake = snake.lower()
        for candidate in (stripped, compact, snake, lower_snake):
            if candidate and candidate not in variants:
                variants.append(candidate)
        return variants

    def local(self, field: str, **kwargs: Any) -> LocalStr:
        """Resolve power localization through canonical key plus compatibility aliases."""
        candidates = []

        localization_key = getattr(self, "localization_key", None)
        if localization_key:
            candidates.append(f"{localization_key}.{field}")

        candidates.append(self._get_localized_key(field))

        name = getattr(self, "name", None)
        if isinstance(name, str):
            for variant in self._normalized_name_candidates(name):
                candidates.append(f"{self.localization_prefix}.{variant}.{field}")

        unique_candidates = []
        for candidate in candidates:
            if candidate not in unique_candidates:
                unique_candidates.append(candidate)

        resolved_key = next(
            (candidate for candidate in unique_candidates if has_translation(candidate)),
            unique_candidates[0],
        )

        default = getattr(self, field, None)
        if default is None:
            default = name if field == "name" and isinstance(name, str) else self.__class__.__name__

        return LocalStr(key=resolved_key, default=default, **kwargs)
    
    @property
    def stackable(self) -> bool:
        """Derive stackable from stack_type for backward compatibility."""
        return self.stack_type not in (StackType.PRESENCE, StackType.MULTI_INSTANCE)
    
    @property
    def idstr(self) -> str:
        """Return class name as ID string."""
        return self.__class__.__name__
    
    @property
    def amount(self) -> int:
        """Effect magnitude."""
        if self.amount_equals_duration:
            return self.duration
        return self._amount
    
    @amount.setter
    def amount(self, value: int):
        normalized = max(0, int(value))
        self._amount = normalized
        if self.amount_equals_duration:
            self._duration = normalized
        
    @property
    def duration(self) -> int:
        """Duration of the power."""
        return self._duration
    
    @duration.setter
    def duration(self, value: int):
        # Allow -1 for permanent powers, clamp other negative values to 0
        if value == -1:
            self._duration = -1  # Permanent power (infinite duration)
        else:
            self._duration = max(0, int(value))
        if self.amount_equals_duration:
            self._amount = self._duration
            
    def tick(self) -> bool:
        """Decrease duration by 1. Returns True if power should be removed."""
        # Permanent powers (duration=-1) should never be decremented or removed
        if self.duration == -1:
            return False
        if self.duration is not None and self.duration != 0:
            # Check if it's a special duration like "turn_start"/"turn_end"
            if not isinstance(self.duration, int):
                return False
            
            self.duration -= 1
            return self.duration <= 0
        return False
    
    @subscribe(PlayerTurnStartedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_turn_start(self):
        """Called at start of turn.
        
        Returns:
            List of actions to execute at turn start
        """
        return

    @subscribe(PlayerTurnPostDrawMessage, priority=MessagePriority.PLAYER_POWER)
    def on_turn_start_post_draw(self):
        """Called after the normal start-of-turn draw resolves."""
        return
    
    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_turn_end(self):
        """Called at end of turn."""
        # tick_down should be called by on_turn_end - decrease duration
        self.tick()
        
        return
    
    @subscribe(CardPlayedMessage, priority=MessagePriority.REACTION)
    def on_card_play(self, card, targets):
        """Called when a card is played.
        
        Returns:
            List of actions to execute after card is played
        """
        return

    @subscribe(CardPlayedMessage, priority=MessagePriority.REACTION)
    def on_play_card(self, card, targets):
        """Compatibility alias for card-play triggers."""
        return
    
    @subscribe(DamageDealtMessage, priority=MessagePriority.REACTION)
    def on_damage_dealt(self, damage: int, target: Any, source: Any = None, card: Any = None, damage_type: str = "direct"):
        """Called when damage is dealt.
        
        Args:
            damage: Original damage amount
            target: Target of the damage
            source: Source of the damage (creature/card)
            card: Card being played (if applicable)
            
        Returns:
            List of actions to execute when damage is dealt
        """
        return
    
    @subscribe(AttackPerformedMessage, priority=MessagePriority.REACTION)
    def on_attack(self, target: Any, source: Any = None, card: Any = None):
        """Called when an attack is performed (before damage calculation).
        
        This hook is called when an attack action is executed, regardless of 
        whether damage is actually dealt (e.g., blocked attacks still trigger this).
        Useful for effects like Thievery that trigger on attack, not on damage.
        
        Args:
            target: Target of the attack
            source: Source of the attack (creature)
            card: Card being played (if applicable)
            
        Returns:
            List of actions to execute when attacking
        """
        return
    
    @subscribe(PhysicalAttackTakenMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_taken(
        self,
        damage: int,
        source: Any = None,
        card: Any = None,
        damage_type: str = "physical",
    ):
        """Called when physical attack damage is taken."""
        return

    @subscribe(PhysicalAttackDealtMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_dealt(
        self,
        damage: int,
        target: Any = None,
        source: Any = None,
        card: Any = None,
        damage_type: str = "physical",
    ):
        """Called when physical attack damage is dealt."""
        return
    
    @subscribe(BlockGainedMessage, priority=MessagePriority.REACTION)
    def on_gain_block(self, amount: int, source: Any = None, card: Any = None):
        """Called when block is gained.
        
        Returns:
            List of actions to execute when block is gained
        """
        return
    
    @subscribe(DirectHpLossMessage, priority=MessagePriority.REACTION)
    def on_direct_hp_loss(self, amount: int, source: Any = None, card: Any = None):
        """Called when direct HP loss resolves."""
        return

    @subscribe(AnyHpLostMessage, priority=MessagePriority.REACTION)
    def on_any_hp_lost(self, amount: int, source: Any = None, card: Any = None):
        """Called whenever actual HP is lost."""
        return
    
    @subscribe(CardDrawnMessage, priority=MessagePriority.PLAYER_POWER)
    def on_card_draw(self, card: Any):
        """Called when a card is drawn.
        
        Args:
            card: The card that was just drawn
            
        Returns:
            List of actions to execute when card is drawn
        """
        return

    @subscribe(CardDrawnMessage, priority=MessagePriority.PLAYER_POWER)
    def on_draw_card(self, card: Any):
        """Called when a card is drawn, with owner context."""
        return

    @subscribe(CardExhaustedMessage, priority=MessagePriority.REACTION)
    def on_card_exhausted(self, card: Any, source_pile: str | None = None):
        """Called when a card is exhausted."""
        return

    @subscribe(PowerAppliedMessage, priority=MessagePriority.REACTION)
    def on_power_added(self, power, target=None):
        """Called when a power is applied."""
        return

    @subscribe(HealedMessage, priority=MessagePriority.REACTION)
    def on_heal(self, amount: int, source: Any = None):
        """Called when healing occurs."""
        return

    @subscribe(CardDiscardedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_discard(self, card: Any):
        """Called when a card is discarded."""
        return
    
    @subscribe(CombatEndedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_combat_end(self):
        """Called at end of combat.
        
        Returns:
            List of actions to execute at combat end
        """
        return
    
    def info(self):
        """
        获取力量的完整信息显示
        
        根据 StackType 决定显示内容：
        - INTENSITY: 只显示 amount
        - DURATION, LINKED: 只显示 duration
        - BOTH, MULTI_INSTANCE: 同时显示 amount 和 duration
        - PRESENCE: 都不显示
        """
        power_type = t('ui.buff', 'Buff') if self.is_buff else t('ui.debuff', 'Debuff')
        name = self.local("name")
        description = self.local("description", amount=self.amount, duration=self.duration)
        
        # 根据 StackType 决定显示内容
        if self.stack_type == StackType.INTENSITY:
            # 只打印 amount
            return f"{name} ({t('ui.type_label', 'Type: {type}', type=power_type)}, {t('ui.amount_label', 'Amount: {amount}', amount=self.amount)})\n{description}"
        elif self.stack_type in (StackType.DURATION, StackType.LINKED):
            # 只打印 duration
            duration_str = t('ui.permanent', 'Permanent') if self.duration == -1 else str(self.duration)
            return f"{name} ({t('ui.type_label', 'Type: {type}', type=power_type)}, {t('ui.duration_label', 'Duration: {duration}', duration=duration_str)})\n{description}"
        elif self.stack_type in (StackType.BOTH, StackType.MULTI_INSTANCE):
            # 都打印
            duration_str = t('ui.permanent', 'Permanent') if self.duration == -1 else str(self.duration)
            return f"{name} ({t('ui.type_label', 'Type: {type}', type=power_type)}, {t('ui.duration_label', 'Duration: {duration}', duration=duration_str)}, {t('ui.amount_label', 'Amount: {amount}', amount=self.amount)})\n{description}"
        else:  # PRESENCE
            # 都不打印
            return f"{name} ({t('ui.type_label', 'Type: {type}', type=power_type)})\n{description}"
