"""SpikeSlime specific intentions."""

import random
from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class LickIntention(Intention):
    """Lick - Applies 2 Frail."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("lick", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Lick: applies 2 Frail to player."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            ApplyPowerAction(
                power="Frail",
                target=game_state.player,
                amount=2,
                duration=2
            )
        ]


class FlameTackleIntention(Intention):
    """Flame Tackle - Deals 16 damage and adds 2 Slimed cards to discard."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("flame_tackle", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Flame Tackle: deals 16 damage and adds Slimed cards."""
        from actions.combat import DealDamageAction
        from actions.card import AddCardAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        actions = [
            DealDamageAction(
                name="Flame Tackle",
                damage=16,
                target=game_state.player,
                damage_type="attack",
                source=self.enemy
            )
        ]
        
        # Add 2 Slimed cards to discard pile
        # Note: Slimed card needs to exist in card registry
        try:
            from utils.registry import get_registered
            SlimedCard = get_registered("card", "Slimed")
            if SlimedCard:
                actions.append(AddCardAction(card=SlimedCard(), dest_pile="discard"))
                actions.append(AddCardAction(card=SlimedCard(), dest_pile="discard"))
        except:
            # If Slimed card doesn't exist, just deal damage
            pass
        
        return actions


class SplitIntention(Intention):
    """Split - Disappears and spawns 2 Spike Slimes (M) with current HP."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Split: spawns 2 smaller slimes."""
        from actions.combat import RemoveEnemyAction, AddEnemyAction
        
        # Current HP will be divided between the two new slimes
        current_hp = self.enemy.hp
        
        actions = [
            RemoveEnemyAction(enemy=self.enemy),
        ]
        
        # Spawn 2 Spike Slimes (M) with half current HP each
        # Note: This assumes SpikeSlimeM class exists
        try:
            from enemies.act1.spike_slime import SpikeSlimeM
            slime_m1 = SpikeSlimeM()
            slime_m1.hp = max(1, current_hp // 2)
            slime_m2 = SpikeSlimeM()
            slime_m2.hp = max(1, current_hp - current_hp // 2)
            
            actions.append(AddEnemyAction(enemy=slime_m1))
            actions.append(AddEnemyAction(enemy=slime_m2))
        except:
            # If SpikeSlimeM doesn't exist yet, just remove the original
            pass
        
        return actions