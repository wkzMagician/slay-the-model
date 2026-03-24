"""Base creature entity shared by player and enemies."""

from typing import List, Optional, TYPE_CHECKING, Any

from engine.messages import (
    BlockGainedMessage,
    CreatureDiedMessage,
    DamageResolvedMessage,
    HealedMessage,
    HpLostMessage,
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

    @subscribe(DamageResolvedMessage, priority=MessagePriority.REACTION)
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type=None):
        """Legacy compatibility hook for subclasses.

        Runtime power reactions are handled by message publication in the damage
        action path. Subclasses may still override this hook for local behavior.
        """
        return []

    def add_power(self, power) -> None:
        """Add a power to this creature with correct stacking semantics."""
        if not power:
            return
        
        from powers.base import StackType
        
        for existing in self.powers:
            if existing.name == power.name:
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

    def remove_power(self, power_name: str) -> None:
        # print(f"[DEBUG] remove_power called: power_name={power_name}, current powers={[p.name for p in self.powers]}")
        self.powers = [p for p in self.powers if p.name != power_name and p.__class__.__name__ != power_name]
        # Also try to match by removing the "Power" suffix
        import re
        base_name = re.sub(r"Power$", "", power_name)
        self.powers = [p for p in self.powers if p.name != base_name]
        # print(f"[DEBUG] After removal: powers={[p.name for p in self.powers]}")

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
    def on_heal(self, amount: int) -> List['Action']:
        """Called when creature heals.
        
        Args:
            amount: Amount of healing
            
        Returns:
            List of actions to queue after healing
        """
        return []

    @subscribe(HpLostMessage, priority=MessagePriority.REACTION)
    def on_lose_hp(self, amount: int, source=None, card=None) -> List['Action']:
        """Legacy compatibility hook for subclasses.

        Runtime HP-loss reactions are handled by message publication in the
        lose-HP action path. Subclasses may still override this hook.
        """
        return []

    @subscribe(DamageResolvedMessage, priority=MessagePriority.REACTION)
    def on_damage_dealt(self, damage: int, target=None, card=None, damage_type: str = "direct") -> List['Action']:
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
    def on_power_added(self, power) -> List['Action']:
        """Legacy compatibility hook for subclasses.

        Runtime power-added reactions are handled by message publication in the
        power application path. Subclasses may still override this hook.
        """
        return []
