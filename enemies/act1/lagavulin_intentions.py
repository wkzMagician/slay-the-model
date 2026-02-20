"""Lagavulin elite enemy intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class SleepIntention(Intention):
    """Sleep - Does nothing while regenerating."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("sleep", enemy)
    
    def execute(self) -> List['Action']:
        """Sleep: do nothing."""
        return []


class StunnedIntention(Intention):
    """Stunned - Does nothing for one turn."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("stunned", enemy)
    
    def execute(self) -> List['Action']:
        """Stunned: do nothing."""
        return []


class AttackIntention(Intention):
    """Attack - Deals 18 damage (10 on A9+)."""
    
    def __init__(self, enemy: 'Enemy', damage: int = 18):
        super().__init__("attack", enemy)
        self.base_damage = damage
    
    def execute(self) -> List['Action']:
        """Execute Attack: deals damage to player."""
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


class SiphonSoulIntention(Intention):
    """Siphon Soul - Player loses 1 Dexterity (2 on A18+), Lagavulin gains 1 Strength (2 on A18+)."""
    
    def __init__(self, enemy: 'Enemy', dex_loss: int = 1, str_gain: int = 1):
        super().__init__("siphon_soul", enemy)
        self.dex_loss = dex_loss
        self.str_gain = str_gain
    
    def execute(self) -> List['Action']:
        """Execute Siphon Soul: player loses Dexterity, Lagavulin gains Strength."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        actions = []
        
        if game_state and game_state.player:
            # Player loses Dexterity
            actions.append(
                ApplyPowerAction(
                    power="Dexterity",
                    target=game_state.player,
                    amount=-self.dex_loss,
                    duration=-1  # Permanent
                )
            )
        
        # Lagavulin gains Strength
        actions.append(
            ApplyPowerAction(
                power="strength",
                target=self.enemy,
                amount=self.str_gain,
                duration=-1  # Permanent
            )
        )
        
        return actions
