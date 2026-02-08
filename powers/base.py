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
    localizable_fields = ("name", "description")
    
    # Power behavior
    stackable: bool = True  # Can multiple instances stack?
    amount_equals_duration: bool = False  # Should amount be set to duration on apply?
    is_buff: bool = True  # True for beneficial effects, False for harmful effects
    
    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """Initialize power with amount and duration.
        
        Args:
            amount: Effect magnitude
            duration: How long the power lasts
            owner: The creature that has this power
        """
        self._amount = amount
        self._duration = duration
        self.owner = owner
        self.stackable = self.__class__.stackable
        self.amount_equals_duration = self.__class__.amount_equals_duration
        self.is_buff = self.__class__.is_buff
    
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
        self._amount = max(0, int(value))
        
    @property
    def duration(self) -> int:
        """Duration of the power."""
        return self._duration
    
    @duration.setter
    def duration(self, value: int):
        self._duration = max(0, int(value))
        if self.amount_equals_duration:
            self._amount = self._duration
            
    def tick(self) -> bool:
        """Decrease duration by 1. Returns True if power should be removed."""
        if self.duration is not None and self.duration != 0:
            # Check if it's a special duration like "turn_start"/"turn_end"
            if not isinstance(self.duration, int):
                return False
            
            self.duration -= 1
            return self.duration <= 0
        return False
    
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
    
    def on_combat_end(self, owner, entities) -> List[Action]:
        """Called at end of combat.
        
        Returns:
            List of actions to execute at combat end
        """
        return []
