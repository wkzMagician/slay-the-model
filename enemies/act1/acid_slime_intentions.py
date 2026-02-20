"""Acid Slime specific intentions."""

from typing import List, TYPE_CHECKING
import random

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class CorrosiveSpitIntention(Intention):
    """Corrosive Spit - Deals damage and adds Slimed cards to discard pile.
    
    Acid Slime (L): 11 damage, 2 Slimed cards (12 damage on A7+)
    Acid Slime (M): 7 damage, 1 Slimed card (8 damage on A3+)
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("corrosive_spit", enemy)
        # Determine damage based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self.base_damage = 11
                self._slimed_count = 2
            elif enemy_class == 'AcidSlimeM':
                self.base_damage = 7
                self._slimed_count = 1
            else:
                self.base_damage = 7
                self._slimed_count = 1
        else:
            self.base_damage = 7
            self._slimed_count = 1
    
    def execute(self) -> List['Action']:
        """Execute Corrosive Spit: deals damage and adds Slimed cards."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from engine.game_state import game_state
        from utils.registry import get_registered
        
        if not game_state or not game_state.player:
            return []
        
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
        
        # Add Slimed cards to discard pile
        try:
            SlimedCard = get_registered("card", "Slimed")
            if SlimedCard:
                for _ in range(self._slimed_count):
                    actions.append(AddCardAction(
                        card=SlimedCard(), 
                        dest_pile="discard_pile", 
                        source="enemy"
                    ))
        except Exception:
            pass
        
        return actions


class LickIntention(Intention):
    """Lick - Applies Weak to player.
    
    Acid Slime (L): 2 Weak
    Acid Slime (M): 1 Weak
    Acid Slime (S): 1 Weak
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("lick", enemy)
        # Determine Weak amount based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self._weak_amount = 2
            else:
                self._weak_amount = 1
        else:
            self._weak_amount = 1
    
    def execute(self) -> List['Action']:
        """Execute Lick: applies Weak to player."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            ApplyPowerAction(
                power="Weak",
                target=game_state.player,
                amount=self._weak_amount,
                duration=2
            )
        ]


class TackleIntention(Intention):
    """Tackle - Deals damage to player.
    
    Acid Slime (L): 16 damage (18 on A3+)
    Acid Slime (M): 10 damage (12 on A3+)
    Acid Slime (S): 3 damage (4 on A3+)
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("tackle", enemy)
        # Determine damage based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self.base_damage = 16
            elif enemy_class == 'AcidSlimeM':
                self.base_damage = 10
            else:  # AcidSlimeS
                self.base_damage = 3
        else:
            self.base_damage = 10
    
    def execute(self) -> List['Action']:
        """Execute Tackle: deals damage to player."""
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


class SplitIntention(Intention):
    """Split - Disappears and spawns Acid Slime (M) and Spike Slime (S) with current HP.
    
    Only used by Acid Slime (L).
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Split: spawns smaller slimes."""
        from actions.combat import RemoveEnemyAction, AddEnemyAction
        
        current_hp = self.enemy.hp
        
        actions = [
            RemoveEnemyAction(enemy=self.enemy),
        ]
        
        # Spawn Acid Slime (M) and Spike Slime (S) with half current HP each
        try:
            from enemies.act1.acid_slime import AcidSlimeM
            from enemies.act1.spike_slime import SpikeSlimeS
            
            acid_m = AcidSlimeM()
            acid_m.hp = max(1, current_hp // 2)
            acid_m.max_hp = acid_m.hp
            
            spike_s = SpikeSlimeS()
            spike_s.hp = max(1, current_hp - current_hp // 2)
            spike_s.max_hp = spike_s.hp
            
            actions.append(AddEnemyAction(enemy=acid_m))
            actions.append(AddEnemyAction(enemy=spike_s))
        except Exception:
            pass
        
        return actions
