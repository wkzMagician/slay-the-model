"""Mystic specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class AttackIntention(Intention):
    """Attack - Deals 8 damage, applies 2 Frail (9 dmg on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("attack", enemy)
        self.base_damage = 8
        self.frail_stacks = 2
    
    def execute(self) -> List['Action']:
        """Execute Attack: deals damage and applies Frail."""
        from actions.combat import AttackAction, ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
            ApplyPowerAction(
                power="frail",
                target=game_state.player,
                amount=self.frail_stacks,
                duration=1
            )
        ]


class BuffIntention(Intention):
    """Buff - All enemies gain 2 Strength (2 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("buff", enemy)
        self.strength_gain = 2
    
    def execute(self) -> List['Action']:
        """Execute Buff: all enemies gain Strength."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        actions = []
        
        # Buff all enemies
        if game_state and game_state.combat:
            for enemy in game_state.combat.enemies:
                if enemy.hp > 0:
                    actions.append(
                        ApplyPowerAction(
                            power="strength",
                            target=enemy,
                            amount=self.strength_gain,
                            duration=-1
                        )
                    )
        
        return actions


class HealIntention(Intention):
    """Heal - All enemies heal 16 HP (16 on A3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("heal", enemy)
        self.heal_amount = 16
    
    def execute(self) -> List['Action']:
        """Execute Heal: all enemies heal."""
        from actions.combat import HealAction
        from engine.game_state import game_state
        
        actions = []
        
        # Heal all enemies
        if game_state and game_state.combat:
            for enemy in game_state.combat.enemies:
                if enemy.hp > 0:
                    actions.append(
                        HealAction(
                            amount=self.heal_amount,
                            target=enemy
                        )
                    )
        
        return actions
