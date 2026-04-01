"""Enemy intention system - defines what an enemy plans to do."""

import re
from typing import List, TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from localization import Localizable, BaseLocalStr, LocalStr, has_translation

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class Intention(ABC, Localizable):
    """Base class for enemy intentions.

    Each intention defines what an enemy plans to do and queues its effects
    when triggered.
    """
    
    # Localization keys are nested under the owning enemy class.
    localization_prefix = "enemies"
    localizable_fields = ("name", "description")
    
    def __init__(self, name: str, enemy: 'Enemy'):
        self.name = name
        self.enemy = enemy
        
        # Base values populated by subclasses in __init__.
        self.base_damage = 0
        self.base_block = 0
        self.base_strength_gain = 0
        self.base_heal = 0
        self.base_amount = 0  # Generic amount for status effects
        self.base_cards = 0
    
    @abstractmethod
    def execute(self) -> None:
        """Execute this intention and queue its actions."""
        pass
    
    def _get_localized_key(self, field: str) -> str:
        """Build the localization key for a specific intention field.

        Keys are structured as: enemies.{EnemyClass}.intentions.{intention_name}.{field}
        e.g., enemies.Cultist.intentions.ritual.name
        """
        # Get intention name from __dict__ to avoid property recursion
        intention_name = self.__dict__.get('name', 'unknown')
        # Get owner's class name (e.g., "Cultist")
        owner_class = self.enemy.__class__.__name__
        return f"{self.localization_prefix}.{owner_class}.intentions.{intention_name}.{field}"

    @staticmethod
    def _intention_key_candidates(name: str) -> List[str]:
        """Generate common localization variants for runtime intention names."""
        if not name:
            return []
        stripped = name.strip()
        no_bang = stripped.replace("!", "")
        snake = re.sub(r"[^A-Za-z0-9]+", "_", stripped).strip("_")
        snake_no_bang = re.sub(r"[^A-Za-z0-9]+", "_", no_bang).strip("_")
        lower_snake = snake.lower()
        lower_snake_no_bang = snake_no_bang.lower()
        compact = re.sub(r"[^A-Za-z0-9]+", "", stripped)
        compact_no_bang = re.sub(r"[^A-Za-z0-9]+", "", no_bang)
        pascal = "".join(part.capitalize() for part in snake_no_bang.split("_") if part)

        variants = []
        for candidate in (
            stripped,
            no_bang,
            snake,
            snake_no_bang,
            lower_snake,
            lower_snake_no_bang,
            compact,
            compact_no_bang,
            pascal,
        ):
            if candidate and candidate not in variants:
                variants.append(candidate)
        return variants

    def local(self, field: str, **kwargs) -> LocalStr:
        """Resolve intention localization through normalized candidate keys."""
        owner_class = self.enemy.__class__.__name__
        candidates = [
            f"{self.localization_prefix}.{owner_class}.intentions.{variant}.{field}"
            for variant in self._intention_key_candidates(self.__dict__.get("name", "unknown"))
        ]

        resolved_key = next(
            (candidate for candidate in candidates if has_translation(candidate)),
            candidates[0] if candidates else self._get_localized_key(field),
        )
        default = self.name
        return LocalStr(key=resolved_key, default=default, **kwargs)
    
    @property
    def description(self) -> 'BaseLocalStr':
        """Return the localized intention description with dynamic values filled in."""
        # Fill template variables used by the localized description.
        variables = {}
        
        # Damage value.
        if self.base_damage > 0:
            from utils.dynamic_values import resolve_potential_damage
            from engine.game_state import game_state
            player = game_state.player
            variables['damage'] = resolve_potential_damage(self.base_damage, self.enemy, player)
        
        # Block value.
        if self.base_block > 0:
            variables['block'] = self.base_block
        
        # Strength gain.
        if self.base_strength_gain > 0:
            variables['strength_gain'] = self.base_strength_gain
        
        # Healing amount.
        if self.base_heal > 0:
            variables['heal'] = self.base_heal
        
        # Generic amount fields such as base_amount / weak / vulnerable / frail.
        amount = self._get_amount()
        if amount > 0:
            variables['amount'] = amount
        
        # Card count, used by intentions like Corrosive Spit.
        if hasattr(self, 'base_cards') and self.base_cards > 0:
            variables['cards'] = self.base_cards
        
        # Hit count for multi-hit intentions.
        hits = self._get_hits()
        if hits > 1:
            variables['hits'] = hits

        # Some intentions expose metallicize as a dedicated field.
        metallicize = getattr(self, 'base_metallicize', 0)
        if isinstance(metallicize, int) and metallicize > 0:
            variables['metallicize'] = metallicize
        
        # Return a LocalStr carrying the computed variables.
        return self.local("description", **variables)
    
    def _get_amount(self) -> int:
        """Resolve a generic amount field using the common fallback order.

        Priority: base_amount > weak_stacks > vulnerable_stacks > frail_stacks
        """
        candidates = [
            'base_amount',
            'weak_stacks',
            'vulnerable_stacks',
            'frail_stacks',
        ]
        
        for attr in candidates:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, int) and value > 0:
                    return value
        
        return 0
    
    def _get_hits(self) -> int:
        """Resolve hit count using the common fallback attribute order."""
        candidates = [
            'hits',
            'base_hits',
            'base_times',
            '_hits',
        ]
        
        for attr in candidates:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, int) and value > 0:
                    return value
        
        return 0
