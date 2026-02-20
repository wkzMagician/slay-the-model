# -*- coding: utf-8 -*-
"""Looter specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class LooterMugIntention(Intention):
    """Mug - Deals 10 damage (11 on Ascension 7+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("mug", enemy)
        self.base_damage = 11  # Ascension 7+ value
    
    def execute(self) -> List['Action']:
        """Execute Mug: deals damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]


class LooterLungeIntention(Intention):
    """Lunge - Deals 12 damage (14 on Ascension 3+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("lunge", enemy)
        self.base_damage = 14  # Ascension 3+ value
    
    def execute(self) -> List['Action']:
        """Execute Lunge: deals damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]


class LooterSmokeBombIntention(Intention):
    """Smoke Bomb - Gains 6 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("smoke_bomb", enemy)
        self.base_block = 6
    
    def execute(self) -> List['Action']:
        """Execute Smoke Bomb: gains block."""
        from actions.combat import GainBlockAction
        
        return [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy,
                source=self.enemy,
            )
        ]


class LooterEscapeIntention(Intention):
    """Escape - Flees combat with stolen gold."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("escape", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Escape: remove enemy from combat (keeping stolen gold)."""
        from actions.combat import RemoveEnemyAction
        from localization import t
        
        # Print escape message
        print(t("combat.looter_escape", default=f"{self.enemy.name} escapes with your gold!", 
                enemy=self.enemy.name))
        
        return [
            RemoveEnemyAction(enemy=self.enemy)
        ]