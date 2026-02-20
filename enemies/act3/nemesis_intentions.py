"""Nemesis elite enemy intentions."""

import random
from typing import List

from actions.combat import AttackAction
from actions.card import AddCardAction
from cards.colorless.burn import Burn
from enemies.intention import Intention


class TriAttack(Intention):
    """Tri Attack - Deals 6x3 damage (7x3 A17+)."""
    
    def __init__(self, enemy):
        super().__init__("Tri Attack", enemy)
        self.base_damage = 6
    
    def execute(self) -> List:
        """Execute tri attack - 3 hits."""
        from engine.game_state import game_state
        
        damage = self.base_damage + self.enemy.strength
        actions = []
        for _ in range(3):
            actions.append(AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        return actions


class TriBurn(Intention):
    """Tri Burn - Adds 3 Burns to discard pile (4 A17+)."""
    
    def __init__(self, enemy):
        super().__init__("Tri Burn", enemy)
        self.base_amount = 3
    
    def execute(self) -> List:
        """Add Burns to player's discard pile."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_amount):
            actions.append(AddCardAction(
                card=Burn(),
                target=game_state.player,
                dest_pile="discard"
            ))
        return actions


class Scythe(Intention):
    """Scythe - Deals 45 damage."""
    
    def __init__(self, enemy):
        super().__init__("Scythe", enemy)
        self.base_damage = 45
    
    def execute(self) -> List:
        """Execute scythe attack."""
        from engine.game_state import game_state
        
        damage = self.base_damage + self.enemy.strength
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]
