"""Base creature entity shared by player and enemies."""

from typing import List, Optional, TYPE_CHECKING, Any

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
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(self.max_hp, int(value)))

    def take_damage(self, amount: int, source=None, card=None, damage_type: str = "direct") -> int:
        """Take damage after block absorption. Returns actual damage dealt to HP."""
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

    def get_damage_taken_multiplier(self) -> float:
        """Get damage multiplier when this creature takes damage.
        
        Applies Vulnerable (1.5x), Buffer, etc.
        """
        multiplier = 1.0
        for power in self.powers:
            if hasattr(power, 'get_damage_taken_multiplier'):
                multiplier *= power.get_damage_taken_multiplier()
        return multiplier
    
    def try_prevent_damage(self) -> bool:
        """Check if any power can prevent damage (e.g., BufferPower).
        
        Returns True if damage was prevented, False otherwise.
        """
        for power in list(self.powers):
            if hasattr(power, 'try_prevent_damage') and power.try_prevent_damage():
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
        if not power:
            return
        for existing in self.powers:
            if existing.name == power.name and existing.stackable:
                if getattr(power, "amount", 0):
                    existing.amount += power.amount
                if getattr(power, "duration", 0):
                    existing.duration += power.duration
                return
        power.owner = self
        self.powers.append(power)

    def remove_power(self, power_name: str) -> None:
        self.powers = [p for p in self.powers if p.name != power_name]

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

    def on_death(self) -> List['Action']:
        """Called when creature dies. Subclasses can override to return actions.
        
        Returns:
            List of actions to queue after death
        """
        return []

    def on_max_hp_changed(self, old_max: int, new_max: int) -> List['Action']:
        """Called when creature's max HP changes.
        
        Args:
            old_max: Previous max HP value
            new_max: New max HP value
            
        Returns:
            List of actions to queue after max HP change
        """
        return []

    def on_heal(self, amount: int) -> List['Action']:
        """Called when creature heals.
        
        Args:
            amount: Amount of healing
            
        Returns:
            List of actions to queue after healing
        """
        return []

    def on_lose_hp(self, amount: int) -> List['Action']:
        """Called when creature loses HP.
        
        Args:
            amount: Amount of HP lost
            
        Returns:
            List of actions to queue after losing HP
        """
        return []

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

    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Called when this creature takes damage.
        
        Args:
            damage: Damage amount taken
            source: Source of damage
            card: Card that caused the damage (if applicable)
            damage_type: Type of damage
            
        Returns:
            List of actions to queue after taking damage
        """
        return []

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

    def on_power_added(self, power) -> List['Action']:
        """Called when a power is added to this creature.
        
        Args:
            power: The power being added
            
        Returns:
            List of actions to queue after power is added
        """
        return []