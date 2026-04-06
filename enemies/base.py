"""Base enemy class for all monsters in combat."""

from typing import Any, Tuple, Dict, List, Optional, TYPE_CHECKING
import random

from entities.creature import Creature
from engine.messages import CombatStartedMessage, PlayerTurnStartedMessage
from engine.subscriptions import MessagePriority, subscribe
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
        name: Optional[str] = None,
        max_hp: Optional[int] = None,
        damage: Optional[int] = None,
        is_minion: bool = False,
        **kwargs
    ) -> None:
        """
        Initialize enemy.
        
        Args:
            hp_range: Tuple of (min_hp, max_hp) for random HP generation
            name: Optional name override for testing
            max_hp: Optional max HP override for testing (bypasses hp_range)
            damage: Optional base damage for testing
            is_minion: Whether this enemy is a summoned minion (minions don't trigger on_fatal)
        """
        if max_hp is not None:
            actual_max_hp = max_hp
        else:
            min_hp, max_hp_val = hp_range
            actual_max_hp = random.randint(min_hp, max_hp_val)
        super().__init__(max_hp=actual_max_hp)
        
        # Store optional overrides
        self._name_override = name
        self._base_damage = damage
        
        # Minion flag - summoned enemies that shouldn't trigger on_fatal effects
        self.is_minion = is_minion
        
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

    def _resolve_next_intention(self, selection: Any) -> 'Intention':
        """Normalize intention selection results.

        Enemy implementations in this codebase are inconsistent:
        some return an Intention, some return a string key/name, and some
        mutate ``self.current_intention`` directly and return ``None``.
        """
        if selection is None:
            if self.current_intention is not None:
                return self.current_intention
            raise ValueError(f"{self.__class__.__name__} did not select an intention")

        if hasattr(selection, "execute") and hasattr(selection, "name"):
            return selection

        if isinstance(selection, str):
            if selection in self.intentions:
                return self.intentions[selection]
            for intention in self.intentions.values():
                if intention.name == selection:
                    return intention
            raise KeyError(
                f"{self.__class__.__name__} selected unknown intention '{selection}'"
            )

        raise TypeError(
            f"Unsupported intention selection type for {self.__class__.__name__}: "
            f"{type(selection).__name__}"
        )
    
    def execute_intention(self) -> None:
        """Execute the current intention."""
        if not self.current_intention:
            return
        
        # Record in history
        if self.current_intention.name not in self.history_intentions:
            self.history_intentions.append(self.current_intention.name)
        else:
            self.history_intentions.append(self.current_intention.name)
        
        self.current_intention.execute()
    
    @subscribe(CombatStartedMessage, priority=MessagePriority.ENEMY)
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts.
        
        Args:
            floor: Current floor number
        """
        # Set initial intention when combat starts
        selection = self.determine_next_intention(floor)
        self.current_intention = self._resolve_next_intention(selection)
    
    @subscribe(PlayerTurnStartedMessage, priority=MessagePriority.ENEMY)
    def on_player_turn_start(self) -> None:
        """Called at the start of player's turn.
        
        Determines the next intention to use.
        """
        from engine.game_state import game_state
        combat_state = getattr(getattr(game_state, "current_combat", None), "combat_state", None)
        if getattr(combat_state, "preserve_enemy_intent_once", False):
            return
        current_floor = game_state.current_floor if game_state else 1
        selection = self.determine_next_intention(current_floor)
        self.current_intention = self._resolve_next_intention(selection)
    
    def on_damage_taken(self, damage: int, source=None, card=None, damage_type=None) -> None:
        """Called when enemy takes damage.
        
        Can be used to trigger special behaviors like splitting at 50% HP.
        
        Args:
            damage: Amount of damage being taken
            source: Source of damage
            card: Card that caused damage
            damage_type: Type of damage
            
        """
        # Override in subclasses for special behaviors
    
    def info(self) -> str:
        """Display current enemy info for displaying in game.
        Including name, hp,intention:name+description.
        """        
        intention_info = f"Intention: {self.current_intention.name} - {self.current_intention.description}" if self.current_intention else "No intention"
        return f"{self.name} - HP: {self.hp}/{self.max_hp} - {intention_info}"
    
    def on_death(self) -> None:
        """Called when enemy dies.

        Subclasses can override this for additional death behavior.
        """
        super().on_death()
