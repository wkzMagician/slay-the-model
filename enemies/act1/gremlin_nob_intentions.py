"""Gremlin Nob elite enemy intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class BellowIntention(Intention):
    """Bellow - Gain 2 Enrage (Enrage: +Strength when playing Skills)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("bellow", enemy)
        self.base_amount = 2
    
    def execute(self) -> List['Action']:
        """Execute Bellow: gain 2 Enrage."""
        from actions.combat import ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="Enrage",
                target=self.enemy,
                amount=2,
                duration=-1  # Permanent
            )
        ]


class SkullBashIntention(Intention):
    """Skull Bash - Deals 6 damage (8 on A9+), applies 2 Vulnerable."""
    
    def __init__(self, enemy: 'Enemy', damage: int = 6):
        super().__init__("skull_bash", enemy)
        self.base_damage = damage
        self.vulnerable_stacks = 2
    
    def execute(self) -> List['Action']:
        """Execute Skull Bash: deal damage and apply Vulnerable."""
        from actions.combat import AttackAction, ApplyPowerAction
        from engine.game_state import game_state
        
        actions = []
        
        if game_state and game_state.player:
            # Deal damage
            actions.append(
                AttackAction(
                    damage=self.base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            )
            # Apply Vulnerable
            actions.append(
                ApplyPowerAction(
                    power="Vulnerable",
                    target=game_state.player,
                    amount=self.vulnerable_stacks,
                    duration=self.vulnerable_stacks
                )
            )
        
        return actions


class BullRushIntention(Intention):
    """Bull Rush - Deals 14 damage (18 on A9+)."""
    
    def __init__(self, enemy: 'Enemy', damage: int = 14):
        super().__init__("bull_rush", enemy)
        self.base_damage = damage
    
    def execute(self) -> List['Action']:
        """Execute Bull Rush: deal damage."""
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
