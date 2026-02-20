"""Spire Spear Elite intentions for Act 4."""

from typing import List
from actions.combat import AttackAction
from enemies.intention import Intention


class Skewer(Intention):
    """Deals 13 damage 3 times."""
    
    def __init__(self, enemy):
        super().__init__("Skewer", enemy)
        self.base_damage = 13
        self.hits = 3
    
    def execute(self) -> List:
        from engine.game_state import game_state
        actions = []
        damage = self.enemy.calculate_damage(self.base_damage)
        for _ in range(self.hits):
            actions.append(AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack"))
        return actions


class SearingBurn(Intention):
    """Adds 3 Burn cards to discard pile."""
    
    def __init__(self, enemy):
        super().__init__("Searing Burn", enemy)
        self.burn_count = 3
    
    def execute(self) -> List:
        from cards.colorless.burn import Burn
        from engine.game_state import game_state
        from actions.combat import AddCardAction
        
        actions = []
        for _ in range(self.burn_count):
            burn = Burn()
            actions.append(AddCardAction(card=burn, target_pile="discard_pile"))
        return actions


class Pierce(Intention):
    """Deals 24 damage."""
    
    def __init__(self, enemy):
        super().__init__("Pierce", enemy)
        self.base_damage = 24
    
    def execute(self) -> List:
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage=damage, target=game_state.player, source=self.enemy, damage_type="attack")]
