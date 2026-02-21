"""Time Eater Boss intentions for Act 3."""

import random
from typing import List

from actions.combat import (
    AttackAction,
    GainBlockAction,
    ApplyPowerAction,
)
from enemies.intention import Intention


class Reverberate(Intention):
    """Deals 7x3 damage."""
    
    def __init__(self, enemy):
        super().__init__("Reverberate", enemy)
        self.base_damage = 7
        self.base_hits = 3
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        return actions


class HeadSlam(Intention):
    """Deals 26 damage. Applies 1 Draw Reduction."""
    
    def __init__(self, enemy):
        super().__init__("Head Slam", enemy)
        self.base_damage = 26
        self.base_draw_reduction = 1
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ),
            ApplyPowerAction(
                power="draw_reduction",
                target=game_state.player,
                amount=self.base_draw_reduction,
                duration=self.base_draw_reduction
            )
        ]
        return actions


class Ripple(Intention):
    """Gains 20 block. Applies 1 Vulnerable and 1 Weak."""
    
    def __init__(self, enemy):
        super().__init__("Ripple", enemy)
        self.base_block = 20
        self.base_amount = 1
    
    def execute(self) -> List:
        """Execute the intention."""
        from engine.game_state import game_state
        
        actions = [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            ),
            ApplyPowerAction(
                power="vulnerable",
                target=game_state.player,
                amount=self.base_amount,
                duration=1
            ),
            ApplyPowerAction(
                power="weak",
                target=game_state.player,
                amount=self.base_amount,
                duration=1
            )
        ]
        return actions


class Haste(Intention):
    """Removes all debuffs. Heals to 50% HP."""
    
    def __init__(self, enemy):
        super().__init__("Haste", enemy)
    
    def execute(self) -> List:
        """Execute the intention."""
        from powers.definitions.strength import StrengthPower
        
        # Remove all powers except StrengthPower
        # (Awakened One retains strength through rebirth)
        strength_powers = [
            p for p in self.enemy.powers 
            if isinstance(p, StrengthPower)
        ]
        self.enemy.powers.clear()
        self.enemy.powers.extend(strength_powers)
        
        # Heal to 50% HP
        heal_amount = self.enemy.max_hp // 2
        self.enemy.heal(heal_amount)
        # Mark that haste was used
        self.enemy._haste_used = True
        return []
