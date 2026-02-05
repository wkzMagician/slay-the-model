"""
Enemy implementations for Slay the Spire clone.
"""
from typing import Optional
from entities.enemy import Enemy
from utils.registry import register


@register("enemy")
class Cultist(Enemy):
    """Weak basic enemy - low damage cultist."""
    
    def __init__(self) -> None:
        super().__init__(
            name="Cultist",
            max_hp=24,
            damage=6,
            is_elite=False,
            is_boss=False
        )
        # Cultists are weak - 25% less effective damage
        self.weak = True


@register("enemy")
class JawWorm(Enemy):
    """Weak but fast enemy."""
    
    def __init__(self) -> None:
        super().__init__(
            name="Jaw Worm",
            max_hp=28,
            damage=5,
            is_elite=False,
            is_boss=False
        )
        # Jaw Worms are weak - 20% less effective damage
        self.weak = True


@register("enemy")
class FungalBeast(Enemy):
    """Medium enemy - fungal creature."""
    
    def __init__(self) -> None:
        super().__init__(
            name="Fungal Beast",
            max_hp=42,
            damage=8,
            is_elite=False,
            is_boss=False
        )
        # Standard enemy - no modifiers
        self.weak = False


@register("enemy")
class Sentry(Enemy):
    """Strong elite enemy - tower guardian."""
    
    def __init__(self) -> None:
        super().__init__(
            name="Sentry",
            max_hp=82,
            damage=12,
            is_elite=True,
            is_boss=False
        )
        # Sentry is strong - deals 25% more damage
        self.strength = 2


@register("enemy")
class Slaver(Enemy):
    """Boss enemy - final boss of the tower."""
    
    def __init__(self) -> None:
        super().__init__(
            name="Slaver",
            max_hp=250,
            damage=18,
            is_elite=False,
            is_boss=True
        )
        # Slaver is boss - deals 50% more damage
        self.strength = 4
        # Boss has artifact damage reduction
        self.artifact = 3
