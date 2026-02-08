"""
Power base class for combat effects.
Powers modify creature stats, damage calculations, and combat flow.
"""
from typing import List, Optional, Any
from actions.base import Action
from localization import Localizable
from utils.types import TargetType


class Power(Localizable):
    """Base power class for temporary and permanent combat effects."""
    
    # Localization
    localization_prefix = "powers"
    
    # Power configuration
    name: str = ""
    description: str = ""
    duration: int = 0  # Number of turns or special values like "turn_start"/"turn_end"
    amount: int = 0  # Effect magnitude
    
    # Power behavior
    stackable: bool = True  # Can multiple instances stack?
    duration_equals_amount: bool = False  # Should duration be set to amount on apply?
    
    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """Initialize power with amount and duration.
        
        Args:
            amount: Effect magnitude
            duration: How long the power lasts
            owner: The creature that has this power
        """
        self.amount = amount if amount != 0 else self.__class__.amount
        self.duration = duration if duration != 0 else self.__class__.duration
        self.owner = owner
        self.name = self.__class__.name or self.idstr
        self.description = self.__class__.description
        self.stackable = self.__class__.stackable
        self.duration_equals_amount = self.__class__.duration_equals_amount
        self.amount = amount
        self.duration = duration
        
        # If duration_equals_amount, sync duration with amount
        if self.duration_equals_amount and self.amount:
            self.duration = self.amount
    
    @property
    def idstr(self) -> str:
        """Return class name as ID string."""
        return self.__class__.__name__
    
    def apply(self, owner=None) -> None:
        """Apply the power to the target creature.
        
        Args:
            owner: The creature to apply the power to
        """
        self.owner = owner or self.owner
        if self.owner:
            # Apply amount if it modifies a stat
            self._apply_amount()
    
    def remove(self) -> None:
        """Remove the power from the creature."""
        if self.owner:
            # Reverse the amount if it modified a stat
            self._remove_amount()
            # Remove from powers list
            self.owner.remove_power(self.name)
    
    def _apply_amount(self) -> None:
        """Apply the power's amount to the owner's stats."""
        pass
    
    def _remove_amount(self) -> None:
        """Remove the power's amount from the owner's stats."""
        pass
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Called at start of player's turn.
        
        Returns:
            List of actions to execute at turn start
        """
        return []
    
    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Called at end of player's turn.
        
        Returns:
            List of actions to execute at turn end
        """
        return []
    
    def on_enemy_turn_start(self, enemy, player, entities) -> List[Action]:
        """Called at start of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn start
        """
        return []
    
    def on_enemy_turn_end(self, enemy, player, entities) -> List[Action]:
        """Called at end of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn end
        """
        return []
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """Called when a card is played.
        
        Returns:
            List of actions to execute after card is played
        """
        return []
    
    def on_damage_dealt(self, damage: int, target: Any, source: Any = None, card: Any = None) -> List[Action]:
        """Called when damage is dealt.
        
        Args:
            damage: Original damage amount
            target: Target of the damage
            source: Source of the damage (creature/card)
            card: Card being played (if applicable)
            
        Returns:
            List of actions to execute when damage is dealt
        """
        return []
    
    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None, 
                       player: Any = None, damage_type: str = "direct") -> List[Action]:
        """Called when damage is taken.
        
        Args:
            damage: Original damage amount
            source: Source of the damage
            card: Card being played (if applicable)
            player: Player taking damage
            damage_type: Type of damage
            
        Returns:
            List of actions to execute when damage is taken
        """
        return []
    
    def on_gain_block(self, amount: int, player: Any = None, source: Any = None, card: Any = None) -> List[Action]:
        """Called when block is gained.
        
        Returns:
            List of actions to execute when block is gained
        """
        return []
    
    def tick(self) -> bool:
        """Decrease duration by 1. Returns True if power should be removed."""
        if self.duration is not None and self.duration != 0:
            # Check if it's a special duration like "turn_start"/"turn_end"
            if not isinstance(self.duration, int):
                return False
            
            self.duration -= 1
            return self.duration <= 0
        return False
    
    def on_combat_end(self, owner, entities) -> List[Action]:
        """Called at end of combat.
        
        Returns:
            List of actions to execute at combat end
        """
        return []
