"""Spike Slime specific intentions."""
from engine.runtime_api import add_action, add_actions

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class LickIntention(Intention):
    """Lick - Applies the configured amount of Frail.
    
    According to doc, Spike Slime (S) applies Frail.
    """
    
    def __init__(self, enemy: 'Enemy', frail_amount: int = 2):
        super().__init__("lick", enemy)
        self._frail_amount = frail_amount
        self.base_amount = frail_amount  # For description variable {amount}
    
    def execute(self) -> None:
        """Execute Lick with matching displayed and applied duration."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        add_actions(
        [
            ApplyPowerAction(
                power="Frail",
                target=game_state.player,
                amount=self._frail_amount,
                duration=self._frail_amount
            )
        ]
        )


class TackleIntention(Intention):
    """Tackle - Deals damage to player.
    
    Spike Slime (L): 16 damage
    Spike Slime (M): 10 damage  
    Spike Slime (S): 5 damage (6 on A2+)
    """
    
    def __init__(self, enemy: 'Enemy', slimed_count: int = 0):
        super().__init__("tackle", enemy)
        self.slimed_count = slimed_count
        # Determine damage based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'SpikeSlimeL':
                self.base_damage = 16
            elif enemy_class == 'SpikeSlimeM':
                self.base_damage = 10
            else:  # SpikeSlimeS
                self.base_damage = 5
        else:
            self.base_damage = 5
    
    def execute(self) -> None:
        """Execute Tackle: deals damage to player."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from cards.colorless.slimed import Slimed
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        actions.extend(
            AddCardAction(Slimed(), dest_pile="discard_pile", source="enemy")
            for _ in range(self.slimed_count)
        )
        add_actions(actions)


class SplitIntention(Intention):
    """Split - Disappears and spawns 2 Spike Slimes (M) with current HP.
    
    Only used by Spike Slime (L).
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)
    
    def execute(self) -> None:
        """Execute Split: spawns 2 smaller slimes."""
        from actions.combat import RemoveEnemyAction, AddEnemyAction
        
        current_hp = self.enemy.hp
        
        actions = [
            RemoveEnemyAction(enemy=self.enemy),
        ]
        
        # Spawn 2 Spike Slimes (M); each gets parent's current HP
        try:
            from enemies.act1.spike_slime import SpikeSlimeM
            
            slime_m1 = SpikeSlimeM()
            slime_m1.max_hp = current_hp
            slime_m1.hp = current_hp
            
            slime_m2 = SpikeSlimeM()
            slime_m2.max_hp = current_hp
            slime_m2.hp = current_hp
            
            actions.append(AddEnemyAction(enemy=slime_m1))
            actions.append(AddEnemyAction(enemy=slime_m2))
        except Exception:
            pass
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
