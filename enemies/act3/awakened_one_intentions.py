"""Awakened One Boss intentions for Act 3."""

import random
from typing import List

from actions.combat import (
    AttackAction,
    GainBlockAction,
    ApplyPowerAction,
)
from enemies.intention import Intention


class Slash(Intention):
    """Deals 20 damage."""
    
    def __init__(self, enemy):
        super().__init__("Slash", enemy)
        self.base_damage = 20
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class SoulStrike(Intention):
    """Deals 6x4 damage."""
    
    def __init__(self, enemy):
        super().__init__("Soul Strike", enemy)
        self.base_damage = 6
        self.base_hits = 4
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        actions = []
        damage = self.enemy.calculate_damage(self.base_damage)
        for _ in range(self.base_hits):
            actions.append(AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        return actions


class Rebirth(Intention):
    """Heals to full HP. Removes all debuffs. Loses 1 Curiosity."""
    
    def __init__(self, enemy):
        super().__init__("Rebirth", enemy)
    
    def execute(self) -> List:
        """Execute the intention."""
        # Remove all debuffs
        self.enemy.weak = 0
        self.enemy.vulnerable = 0
        # Heal to full HP
        self.enemy.heal(self.enemy.max_hp)
        # Switch to phase 2
        self.enemy._phase = 2
        return []


class DarkEcho(Intention):
    """Deals 40 damage."""
    
    def __init__(self, enemy):
        super().__init__("Dark Echo", enemy)
        self.base_damage = 40
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class Sludge(Intention):
    """Deals 18 damage. Adds a Wound into your draw pile."""
    
    def __init__(self, enemy):
        super().__init__("Sludge", enemy)
        self.base_damage = 18
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        # TODO: Add Wound to draw pile when card system supports it
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class Tackle(Intention):
    """Deals 10x3 damage."""
    
    def __init__(self, enemy):
        super().__init__("Tackle", enemy)
        self.base_damage = 10
        self.base_hits = 3
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        actions = []
        damage = self.enemy.calculate_damage(self.base_damage)
        for _ in range(self.base_hits):
            actions.append(AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        return actions
