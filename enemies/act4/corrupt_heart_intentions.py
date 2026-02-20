"""Corrupt Heart Boss intentions for Act 4."""

from typing import List
from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention


class Debilitate(Intention):
    """Deals 2x damage (based on unique cards played)."""
    
    def __init__(self, enemy):
        super().__init__("Debilitate", enemy)
        self.multiplier = 2
    
    def execute(self) -> List:
        from engine.game_state import game_state
        # Base damage is number of unique cards played * multiplier
        unique_cards = getattr(self.enemy, 'unique_cards_played', 0)
        damage = unique_cards * self.multiplier
        return [AttackAction(damage=max(damage, 5), target=game_state.player, source=self.enemy, damage_type="attack")]


class AttackHeart(Intention):
    """Deals 45 damage."""
    
    def __init__(self, enemy):
        super().__init__("Attack", enemy)
        self.base_damage = 45
    
    def execute(self) -> List:
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack")]


class BloodShots(Intention):
    """Deals 2 damage 12 times."""
    
    def __init__(self, enemy):
        super().__init__("Blood Shots", enemy)
        self.base_damage = 2
        self.hits = 12
    
    def execute(self) -> List:
        from engine.game_state import game_state
        actions = []
        damage = self.enemy.calculate_damage(self.base_damage)
        for _ in range(self.hits):
            actions.append(AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack"))
        return actions


class Echo(Intention):
    """Gains 2 Strength and 2 passive Block."""
    
    def __init__(self, enemy):
        super().__init__("Echo", enemy)
        self.strength_gain = 2
        self.block_gain = 2
    
    def execute(self) -> List:
        from actions.combat import AddPowerAction, GainBlockAction
        actions = [
            AddPowerAction(power="strength", target=self.enemy, amount=self.strength_gain),
            GainBlockAction(block=self.block_gain, target=self.enemy)
        ]
        return actions


class BuffHeart(Intention):
    """Gains 5 Strength and 15 passive Block."""
    
    def __init__(self, enemy):
        super().__init__("Buff", enemy)
        self.strength_gain = 5
        self.block_gain = 15
    
    def execute(self) -> List:
        from actions.combat import AddPowerAction, GainBlockAction
        actions = [
            AddPowerAction(power="strength", target=self.enemy, amount=self.strength_gain),
            GainBlockAction(block=self.block_gain, target=self.enemy)
        ]
        return actions


class Invoke(Intention):
    """Summons Orbs (for Defect compatibility, simplified here)."""
    
    def __init__(self, enemy):
        super().__init__("Invoke", enemy)
    
    def execute(self) -> List:
        # Simplified: just gains block as placeholder
        return [GainBlockAction(block=10, target=self.enemy)]
