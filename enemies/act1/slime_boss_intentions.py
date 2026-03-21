"""Slime Boss (Boss) specific intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class GoopSprayIntention(Intention):
    """Goop Spray - Adds 3 Slimed cards to discard pile (5 on A19+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("goop_spray", enemy)
        self._slimed_count = 3
    
    def execute(self) -> List['Action']:
        """Execute Goop Spray: adds Slimed cards to discard pile."""
        from actions.card import AddCardAction
        from utils.registry import get_registered
        
        actions = []
        
        try:
            SlimedCard = get_registered("card", "Slimed")
            if SlimedCard:
                for _ in range(self._slimed_count):
                    actions.append(AddCardAction(card=SlimedCard(), dest_pile="discard_pile"))
        except Exception:
            pass
        
        return actions


class PreparingIntention(Intention):
    """Preparing - Does nothing."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("preparing", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Preparing: does nothing."""
        return []


class SlamIntention(Intention):
    """Slam - Deals 35 damage (38 on A4+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("slam", enemy)
        self.base_damage = 35
    
    def execute(self) -> List['Action']:
        """Execute Slam: deals 35 damage to player."""
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
    """Split - Disappears and spawns Acid Slime (L) and Spike Slime (L) with current HP."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Split: spawns two Large Slimes."""
        from actions.combat import RemoveEnemyAction, AddEnemyAction
        
        current_hp = self.enemy.hp
        
        actions = [
            RemoveEnemyAction(enemy=self.enemy),
        ]
        
        # Spawn Acid Slime (L) and Spike Slime (L); each gets parent's current HP
        try:
            from enemies.act1.acid_slime import AcidSlimeL
            from enemies.act1.spike_slime import SpikeSlimeL
            
            acid_slime = AcidSlimeL()
            acid_slime.hp = current_hp
            acid_slime.max_hp = current_hp
            
            spike_slime = SpikeSlimeL()
            spike_slime.hp = current_hp
            spike_slime.max_hp = current_hp
            
            actions.append(AddEnemyAction(enemy=acid_slime))
            actions.append(AddEnemyAction(enemy=spike_slime))
        except Exception:
            pass
        
        return actions
