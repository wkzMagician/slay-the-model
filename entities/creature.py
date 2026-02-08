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
        if self.is_dead():
            actions = self.on_death()
            if actions:
                from engine.game_state import game_state
                game_state.action_queue.add_actions(actions)

    def take_damage(self, amount: int, source=None, card=None, damage_type: str = "direct") -> int:
        """Take damage and reduce HP/block.
        
        This method ONLY handles numerical changes. All power/relic triggers
        should be called by actions (e.g., DealDamageAction in actions/combat.py).
        
        Args:
            amount: Damage amount (already modified by powers/relics)
            source: Source of the damage (for reference only)
            card: Card that caused damage (for reference only)
            damage_type: Type of damage (for reference only)
            
        Returns:
            Actual HP damage dealt (after block absorption)
        """
        if amount <= 0:
            return 0

        absorbed = min(self.block, amount)
        self.block -= absorbed
        remaining = amount - absorbed
        if remaining > 0:
            self.hp -= remaining
        return remaining

    def heal(self, amount: int) -> int:
        if amount <= 0:
            return 0
        self.hp += amount
        return self._hp

    def gain_block(self, amount: int, source=None, card=None) -> None:
        """Gain block.
        
        This method ONLY handles numerical changes. All power/relic triggers
        should be called by actions (e.g., GainBlockAction in actions/combat.py).
        
        Args:
            amount: Block amount to gain (already modified by powers/relics)
            source: Source of the block (for reference only)
            card: Card that caused block (for reference only)
        """
        if amount <= 0:
            return
        self.block += amount

    def add_power(self, power) -> None:
        """Add a power to this creature.
        
        This method ONLY handles numerical changes. The on_power_added hook
        should be called by actions (e.g., ApplyPowerAction in actions/combat.py).
        
        Args:
            power: Power instance to add
        """
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
        """Remove a power from this creature.
        
        This method ONLY handles numerical changes. The on_power_removed hook
        should be called by actions.
        
        Args:
            power_name: Name of the power to remove
        """
        self.powers = [p for p in self.powers if p.name != power_name]

    def get_power(self, power_name: str):
        if not power_name:
            return None
        lookup = str(power_name).lower()
        for power in list(self.powers):
            if getattr(power, "name", "").lower() == lookup:
                return power
        return None

    # ==================== Phase Hooks ====================
    
    def on_combat_start(self) -> List['Action']:
        """Called at the start of combat.
        
        Returns:
            List of actions to execute after combat starts
        """
        return []
    
    def on_combat_end(self) -> List['Action']:
        """Called at the end of combat.
        
        Returns:
            List of actions to execute after combat ends
        """
        return []
    
    def on_turn_start(self) -> List['Action']:
        """Called at the start of this creature's turn.
        
        Returns:
            List of actions to execute at turn start
        """
        return []
    
    def on_turn_end(self) -> List['Action']:
        """Called at the end of this creature's turn.
        
        Returns:
            List of actions to execute at turn end
        """
        return []
    
    # ==================== Stat Change Hooks ====================
    
    def on_damage_dealt(self, damage: int, target=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Called when this creature deals damage.
        
        Args:
            damage: Original damage amount
            target: Target of the damage
            card: Card that caused the damage (if applicable)
            damage_type: Type of damage ("direct", "attack", etc.)
            
        Returns:
            List of actions to execute when damage is dealt
        """
        return []
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> List['Action']:
        """Called when this creature takes damage.
        
        Args:
            damage: Original damage amount
            source: Source of the damage
            card: Card that caused damage (if applicable)
            damage_type: Type of damage
            
        Returns:
            List of actions to execute when damage is taken
        """
        return []
    
    def on_heal(self, amount: int) -> List['Action']:
        """Called when this creature is healed.
        
        Args:
            amount: Original heal amount
            
        Returns:
            List of actions to execute when healing occurs
        """
        return []
    
    def on_lose_hp(self, amount: int) -> List['Action']:
        """Called when this creature loses HP (not from combat damage).
        
        Args:
            amount: Original HP loss amount
            
        Returns:
            List of actions to execute when HP is lost
        """
        return []
    
    def on_gain_block(self, amount: int, source=None, card=None) -> List['Action']:
        """Called when this creature gains block.
        
        Args:
            amount: Original block amount
            source: Source of the block
            card: Card that caused block (if applicable)
            
        Returns:
            List of actions to execute when block is gained
        """
        return []
    
    def on_max_hp_changed(self, old_max: int, new_max: int) -> List['Action']:
        """Called when this creature's max HP changes.
        
        Args:
            old_max: Old max HP value
            new_max: New max HP value
            
        Returns:
            List of actions to execute when max HP changes
        """
        return []
    
    # ==================== Power Hooks ====================
    
    def on_power_added(self, power) -> List['Action']:
        """Called when a power is added to this creature.
        
        Args:
            power: Power that was added
            
        Returns:
            List of actions to execute when power is added
        """
        return []
    
    def on_power_removed(self, power_name: str) -> List['Action']:
        """Called when a power is removed from this creature.
        
        Args:
            power_name: Name of the power that was removed
            
        Returns:
            List of actions to execute when power is removed
        """
        return []
    
    # ==================== Death Hook ====================
    
    def on_death(self) -> List['Action']:
        """Called when creature dies. Subclasses can override to return actions.
        
        Returns:
            List of actions to queue after death
        """
        return []
