"""Spire Shield Elite intentions for Act 4."""

from typing import List
from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention


class Bash(Intention):
    """Deals 12 damage and applies 2 Vulnerable."""
    
    def __init__(self, enemy):
        super().__init__("Bash", enemy)
        self.base_damage = 12
        self.base_amount = 2
    
    def execute(self) -> List:
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [
            AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack"),
            ApplyPowerAction(power="vulnerable", target=game_state.player, amount=self.base_amount)
        ]


class Fortify(Intention):
    """Gains 30 block."""
    
    def __init__(self, enemy):
        super().__init__("Fortify", enemy)
        self.base_block = 30
    
    def execute(self) -> List:
        return [GainBlockAction(block=self.base_block, target=self.enemy)]


class Smite(Intention):
    """Deals 18 damage."""
    
    def __init__(self, enemy):
        super().__init__("Smite", enemy)
        self.base_damage = 18
    
    def execute(self) -> List:
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack")]
