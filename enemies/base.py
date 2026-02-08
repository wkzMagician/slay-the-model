"""Base enemy class for all monsters in combat."""

from typing import Tuple, Dict, List, Optional, TYPE_CHECKING
import random

from entities.creature import Creature
from localization import BaseLocalStr
from utils.registry import register
from utils.types import EnemyType

if TYPE_CHECKING:
    from enemies.intention import Intention
    from actions.base import Action


@register("enemy")
class Enemy(Creature):
    """Base enemy class for combat encounters, inherits from Creature.
    
    All specific enemy classes should inherit from this base class.
    Enemies are organized by the act they first appear in (e.g., act1/, act2/).
    """
    
    localizable_fields: Tuple[str, ...] = ("name",)
    localization_prefix: str = "enemies"
    
    enemy_type: EnemyType = EnemyType.NORMAL
    
    def __init__(
        self,
        hp_range: Tuple[int, int] = (40, 50),
    ) -> None:
        """
        Initialize enemy.
        
        Args:
            hp_range: Tuple of (min_hp, max_hp) for random HP generation
        """
        min_hp, max_hp = hp_range
        actual_max_hp = random.randint(min_hp, max_hp)
        super().__init__(max_hp=actual_max_hp)
        
        # Intention system
        self.intentions: Dict[str, 'Intention'] = {}
        self.current_intention: Optional['Intention'] = None
        self.history_intentions: List[str] = []
    
    @property
    def name(self) -> BaseLocalStr:
        """Get localized name of this enemy."""
        return self.local("name")
    
    def __str__(self):
        return f"{self.name} ({self.hp}/{self.max_hp} HP)"
    
    def add_intention(self, intention: 'Intention') -> None:
        """Register an intention for this enemy.
        
        Args:
            intention: Intention instance to add
        """
        self.intentions[intention.name] = intention
    
    def determine_next_intention(self, floor: int = 1) -> 'Intention':
        """Determine the next intention to use.
        
        This method should be overridden by specific enemy classes to implement
        their intention selection logic based on:
        - History of used intentions
        - Current floor
        - Ascension level
        - Enemy-specific conditions (e.g., HP thresholds)
        
        Args:
            floor: Current floor number
            
        Returns:
            The next Intention to execute
        """
        # Default implementation: return first intention or random
        if self.intentions:
            intention_list = list(self.intentions.values())
            if intention_list:
                return random.choice(intention_list)
        raise ValueError("No intentions defined for enemy")
    
    def execute_intention(self) -> List['Action']:
        """Execute the current intention and update history.
        
        Returns:
            List of actions to queue
        """
        if not self.current_intention:
            return []
        
        # Record in history
        if self.current_intention.name not in self.history_intentions:
            self.history_intentions.append(self.current_intention.name)
        else:
            self.history_intentions.append(self.current_intention.name)
        
        # Execute the intention
        actions = self.current_intention.execute()
        return actions
    
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts.
        
        Args:
            floor: Current floor number
        """
        pass
    
    def on_player_turn_start(self) -> None:
        """Called at the start of player's turn.
        
        Determines the next intention to use.
        """
        from engine.game_state import game_state
        current_floor = game_state.current_floor if game_state else 1
        self.current_intention = self.determine_next_intention(current_floor)
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type: str = "direct") -> int:
        """Called when enemy takes damage.
        
        Can be used to trigger special behaviors like splitting at 50% HP.
        
        Args:
            damage: Amount of damage being taken
            source: Source of damage
            card: Card that caused damage
            damage_type: Type of damage
            
        Returns:
            Modified damage amount
        """
        # Override in subclasses for special behaviors
        return damage
    
    def on_death(self) -> List['Action']:
        """Called when enemy dies.
        
        Subclasses can override this to return actions to execute after death.
        
        Returns:
            List of actions to queue after death
        """
        return super().on_death()
