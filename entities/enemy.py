"""
Enemy entity - represents monsters in combat.
"""
from entities.player import Player
from utils.types import RarityType


class Enemy:
    """Base enemy class for combat encounters"""
    
    def __init__(self, name: str, max_hp: int, damage: int = 6, is_elite: bool = False, is_boss: bool = False):
        """
        Initialize enemy.
        
        Args:
            name: Display name of enemy
            max_hp: Maximum HP
            damage: Base damage amount
            is_elite: Whether this is an elite enemy
            is_boss: Whether this is a boss enemy
        """
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.damage = damage
        self.is_elite = is_elite
        self.is_boss = is_boss
        self.is_dead = False
        
        # Combat modifiers (can be modified by relics/status effects)
        self.strength = 0
        self.weak = False
        self.vulnerable = False
        self.artifact = 0  # Reduces debuff duration
    
    def take_damage(self, amount: int, source, damage_type: str = "attack") -> int:
        """
        Take damage.
        
        Args:
            amount: Damage amount (can be negative for healing)
            source: What dealt the damage
            damage_type: Type of damage
        
        Returns:
            Actual damage taken (accounting for armor, etc.)
        """
        # Simplified damage calculation
        # Apply weak if active
        if self.weak:
            amount = int(amount * 0.75)
        
        # Apply artifact if any
        if self.artifact > 0:
            amount = max(0, amount - self.artifact)
        
        actual_damage = max(1, amount)
        self.current_hp -= actual_damage
        
        # Check for death
        if self.current_hp <= 0:
            self.is_dead = True
        
        return actual_damage
    
    def is_dead(self) -> bool:
        """Check if enemy is dead"""
        return self.is_dead or self.current_hp <= 0
    
    def reset_for_combat(self):
        """Reset enemy state at start of combat"""
        self.current_hp = self.max_hp
        self.is_dead = False
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"
