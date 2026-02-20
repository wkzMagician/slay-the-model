"""The Guardian (Boss) specific intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class ChargingUpIntention(Intention):
    """Charging Up - Gains 9 Block."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("charging_up", enemy)
        self.base_block = 9
    
    def execute(self) -> List['Action']:
        """Execute Charging Up: gains 9 Block."""
        from actions.combat import GainBlockAction
        
        return [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            )
        ]


class FierceBashIntention(Intention):
    """Fierce Bash - Deals 32 damage (36 on A4+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("fierce_bash", enemy)
        self.base_damage = 32
    
    def execute(self) -> List['Action']:
        """Execute Fierce Bash: deals 32 damage to player."""
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


class VentSteamIntention(Intention):
    """Vent Steam - Applies 2 Weak and 2 Vulnerable."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("vent_steam", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Vent Steam: applies 2 Weak and 2 Vulnerable to player."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            ApplyPowerAction(
                power="Weak",
                target=game_state.player,
                amount=2,
                duration=2
            ),
            ApplyPowerAction(
                power="Vulnerable",
                target=game_state.player,
                amount=2,
                duration=2
            )
        ]


class WhirlwindIntention(Intention):
    """Whirlwind - Deals 5 damage 4 times."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("whirlwind", enemy)
        self.base_damage = 5
        self._hits = 4
    
    def execute(self) -> List['Action']:
        """Execute Whirlwind: deals 5 damage 4 times."""
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
            for _ in range(self._hits)
        ]


class DefensiveModeIntention(Intention):
    """Defensive Mode - Gains 3 Sharp Hide (4 on A19+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("defensive_mode", enemy)
        self._sharp_hide_stacks = 3
    
    def execute(self) -> List['Action']:
        """Execute Defensive Mode: gains Sharp Hide."""
        from actions.combat import ApplyPowerAction
        
        return [
            ApplyPowerAction(
                power="SharpHide",
                target=self.enemy,
                amount=self._sharp_hide_stacks,
                duration=-1
            )
        ]


class RollAttackIntention(Intention):
    """Roll Attack - Deals 9 damage (10 on A4+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("roll_attack", enemy)
        self.base_damage = 9
    
    def execute(self) -> List['Action']:
        """Execute Roll Attack: deals 9 damage to player."""
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


class TwinSlamIntention(Intention):
    """Twin Slam - Deals 8 damage 2 times. Loses Sharp Hide. Resets Mode Shift."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("twin_slam", enemy)
        self.base_damage = 8
    
    def execute(self) -> List['Action']:
        """Execute Twin Slam: deals 8 damage 2 times and removes Sharp Hide."""
        from actions.combat import AttackAction, RemovePowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
            for _ in range(2)
        ]
        
        # Remove Sharp Hide
        actions.append(
            RemovePowerAction(
                power="SharpHide",
                target=self.enemy
            )
        )
        
        return actions
