"""Base creature entity shared by player and enemies."""

import re
from typing import List, Optional, TYPE_CHECKING, Any

from engine.messages import (
    AnyHpLostMessage,
    BlockGainedMessage,
    CreatureDiedMessage,
    DamageDealtMessage,
    DirectHpLossMessage,
    HealedMessage,
    HpLostMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
    PowerAppliedMessage,
)
from engine.subscriptions import MessagePriority, subscribe
from localization import Localizable

if TYPE_CHECKING:
    from actions.base import Action


class Creature(Localizable):
    """Base creature with health, block, and powers.

    The on_death method allows subclasses to return actions to execute on death.
    """

    def __init__(
        self,
        max_hp: int,
        powers: Optional[List[Any]] = None,
    ) -> None:
        self._max_hp = max_hp
        self._hp = max_hp
        self._block = 0
        self.powers: List[Any] = list(powers or [])

    @staticmethod
    def _power_identity(power: Any) -> str:
        """Canonical key for stacking/lookup decisions."""
        return str(getattr(power, "idstr", power.__class__.__name__))

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        self._hp += value - self._max_hp
        self._max_hp = max(1, int(value))

    @property
    def block(self) -> int:
        return self._block

    @block.setter
    def block(self, value: int) -> None:
        self._block = max(0, int(value))

    def is_dead(self) -> bool:
        return self._hp <= 0

    @property
    def is_alive(self) -> bool:
        return not self.is_dead()

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(self.max_hp, int(value)))

    @property
    def strength(self) -> int:
        """Backward-compatible aggregate Strength value."""
        total = 0
        for power in self.powers:
            power_name = getattr(power, "name", "")
            if power_name == "Strength" or power.__class__.__name__ == "StrengthPower":
                total += int(getattr(power, "amount", 0) or 0)
        return total

    def take_damage(self, amount: int, source=None, card=None, damage_type: str = "direct") -> int:
        """Take damage after block absorption. Returns actual damage dealt to HP."""
        if isinstance(amount, list):
            raise TypeError("take_damage expects int, got list")
        if amount <= 0:
            return 0
        
        damage = amount
        
        # Apply block
        absorbed = min(self.block, damage)
        self.block -= absorbed
        remaining = damage - absorbed
        
        if remaining > 0:
            self.hp -= remaining
        
        return remaining

    def get_damage_dealt_modifier(self, base_damage: int) -> int:
        """Calculate modified damage when this creature deals damage.
        
        Applies Strength, Weakness, etc.
        """
        damage = base_damage
        for power in self.powers:
            if hasattr(power, 'modify_damage_dealt'):
                damage = power.modify_damage_dealt(damage)
        return max(0, damage)

    def calculate_damage(self, base_damage: int) -> int:
        """Backward-compatible alias for outgoing damage calculation."""
        return self.get_damage_dealt_modifier(base_damage)

    def get_damage_taken_multiplier(self) -> float:
        """Get damage multiplier when this creature takes damage.
        
        Applies Vulnerable (1.5x), Buffer, etc.
        """
        multiplier = 1.0
        for power in self.powers:
            if hasattr(power, 'get_damage_taken_multiplier'):
                multiplier *= power.get_damage_taken_multiplier()
        return multiplier
    
    def try_prevent_damage(self, amount: int = 0) -> bool:
        """Check if any power can prevent damage (e.g., BufferPower).
        
        Args:
            amount: Amount of damage to potentially prevent
            
        Returns True if damage was prevented, False otherwise.
        """
        # print(f"[DEBUG] Creature.try_prevent_damage called: amount={amount}, powers={[p.__class__.__name__ for p in self.powers]}")
        for power in list(self.powers):
            if hasattr(power, 'try_prevent_damage'):
                # print(f"[DEBUG] Checking power {power.__class__.__name__} for damage prevention")
                if power.try_prevent_damage(amount):
                    # print(f"[DEBUG] Power {power.__class__.__name__} prevented damage!")
                    return True
        # print(f"[DEBUG] No power prevented damage")
        return False

    def try_prevent_debuff(self) -> bool:
        """Check if any power can prevent a debuff (e.g., ArtifactPower).
        
        Returns True if debuff was prevented, False otherwise.
        """
        for power in list(self.powers):
            if hasattr(power, 'try_prevent_debuff') and callable(power.try_prevent_debuff):
                if power.try_prevent_debuff():
                    return True
        return False

    def heal(self, amount: int) -> int:
        if amount <= 0:
            return 0
        self.hp += amount
        return self._hp

    def gain_block(self, amount: int, source=None, card=None) -> None:
        """Gain block amount. Hooks return actions to be queued by caller.
        
        This method ONLY handles numerical changes. Power/relic on_gain_block
        hooks should be collected and queued by the calling Action.
        """
        if amount <= 0:
            return None
        self.block += amount

    def add_power(self, power) -> None:
        """Add a power to this creature with correct stacking semantics."""
        if not power:
            return
        
        from powers.base import StackType
        power_id = self._power_identity(power)
        
        for existing in self.powers:
            if self._power_identity(existing) == power_id:
                # Handle based on stack type
                if power.stack_type == StackType.PRESENCE:
                    # Presence powers don't stack - refresh duration if longer
                    if power.duration > 0 and power.duration > existing.duration:
                        existing.duration = power.duration
                    return
                
                if power.stack_type == StackType.MULTI_INSTANCE:
                    # Multi-instance powers always create new instances
                    break  # Fall through to append new instance
                
                # Stackable types - merge with existing
                if power.stack_type == StackType.INTENSITY:
                    if power.amount:
                        existing.amount += power.amount
                elif power.stack_type == StackType.DURATION:
                    if power.duration and power.duration > 0:
                        existing.duration += power.duration
                elif power.stack_type == StackType.BOTH:
                    if power.amount:
                        existing.amount += power.amount
                    if power.duration and power.duration > 0:
                        existing.duration += power.duration
                elif power.stack_type == StackType.LINKED:
                    if power.duration and power.duration > 0:
                        existing.duration += power.duration
                    elif power.amount:
                        existing.amount += power.amount
                return
        
        # New power instance
        power.owner = self
        self.powers.append(power)

    def remove_power(self, power_or_name) -> None:
        if power_or_name is None:
            return
        if power_or_name in self.powers:
            self.powers = [p for p in self.powers if p is not power_or_name]
            return

        power_name = str(power_or_name)
        base_name = re.sub(r"Power$", "", power_name)
        self.powers = [
            p for p in self.powers
            if p.name != power_name
            and p.__class__.__name__ != power_name
            and self._power_identity(p) != power_name
            and p.name != base_name
        ]

    def get_power(self, power_name: str):
        if not power_name:
            return None
        lookup = str(power_name).lower()
        for power in list(self.powers):
            if getattr(power, "name", "").lower() == lookup:
                return power
        return None

    def has_power(self, power_name: str) -> bool:
        """Check if this creature has a specific power"""
        return self.get_power(power_name) is not None

    @subscribe(CreatureDiedMessage, priority=MessagePriority.REACTION)
    def on_death(self) -> List['Action']:
        """Called when creature dies. Subclasses can override to return actions.
        
        Returns:
            List of actions to queue after death
        """
        return []

    @subscribe(HealedMessage, priority=MessagePriority.REACTION)
    def on_heal(self, amount: int, source=None) -> List['Action']:
        """Called when creature heals.
        
        Args:
            amount: Amount of healing
            
        Returns:
            List of actions to queue after healing
        """
        return []

    @subscribe(DamageDealtMessage, priority=MessagePriority.REACTION)
    def on_damage_dealt(self, damage: int, target=None, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Called when this creature deals damage.
        
        Args:
            damage: Damage amount dealt
            target: Target creature
            card: Card that caused the damage (if applicable)
            damage_type: Type of damage
            
        Returns:
            List of actions to queue after dealing damage
        """
        return []

    @subscribe(PhysicalAttackTakenMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_taken(
        self,
        damage: int,
        source=None,
        card=None,
        damage_type: str = "physical",
    ) -> List['Action']:
        """Called when this creature loses HP to a physical attack."""
        return []

    @subscribe(PhysicalAttackDealtMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_dealt(
        self,
        damage: int,
        target=None,
        source=None,
        card=None,
        damage_type: str = "physical",
    ) -> List['Action']:
        """Called when this creature deals HP loss via a physical attack."""
        return []

    @subscribe(DirectHpLossMessage, priority=MessagePriority.REACTION)
    def on_direct_hp_loss(self, amount: int, source=None, card=None) -> List['Action']:
        """Called when this creature directly loses HP without damage resolution."""
        return []

    @subscribe(AnyHpLostMessage, priority=MessagePriority.REACTION)
    def on_any_hp_lost(self, amount: int, source=None, card=None) -> List['Action']:
        """Called when this creature loses HP for any reason."""
        return []

    @subscribe(BlockGainedMessage, priority=MessagePriority.REACTION)
    def on_gain_block(self, amount: int, source=None, card=None) -> List['Action']:
        """Called when this creature gains block.
        
        Args:
            amount: Block amount gained
            source: Source of block
            card: Card that caused block (if applicable)
            
        Returns:
            List of actions to queue after gaining block
        """
        return []

    @subscribe(PowerAppliedMessage, priority=MessagePriority.REACTION)
    def on_power_added(self, power, target=None) -> List['Action']:
        """Legacy compatibility hook for subclasses.

        Runtime power-added reactions are handled by message publication in the
        power application path. Subclasses may still override this hook.
        """
        return []
