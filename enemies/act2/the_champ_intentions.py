"""The Champ intentions - Act 2 Elite enemy."""

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention
from powers.base import PowerType

if TYPE_CHECKING:
    from enemies.the_champ import TheChamp


class HeavySlash(Intention):
    """Deals 16 damage."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Heavy Slash", enemy)
        self.base_damage = 16
    
    def execute(self) -> List:
        """Execute heavy slash attack."""
        from engine.game_state import game_state
        
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class FaceSlap(Intention):
    """Deals 12 damage. Applies 2 Frail and 2 Vulnerable."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Face Slap", enemy)
        self.base_damage = 12
        self.base_amount = 2
    
    def execute(self) -> List:
        """Execute face slap - damage and debuffs."""
        from engine.game_state import game_state
        
        actions = []
        player = game_state.player
        
        # Deal damage
        damage = self.enemy.calculate_damage(self.base_damage)
        actions.append(AttackAction(
            damage=damage,
            target=player,
            source=self.enemy,
            damage_type="attack"
        ))
        
        # Apply Frail
        actions.append(ApplyPowerAction(
            power=PowerType.FRAIL,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        # Apply Vulnerable
        actions.append(ApplyPowerAction(
            power=PowerType.VULNERABLE,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        return actions


class DefensiveStance(Intention):
    """Gains 8 Block and 2 Strength."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Defensive Stance", enemy)
        self.base_block = 8
        self.base_strength_gain = 2
    
    def execute(self) -> List:
        """Execute defensive stance."""
        actions = []
        
        # Gain block
        actions.append(GainBlockAction(
            block=self.base_block,
            target=self.enemy
        ))
        
        # Gain strength
        actions.append(ApplyPowerAction(
            power=PowerType.STRENGTH,
            target=self.enemy,
            amount=self.base_strength_gain,
            duration=-1
        ))
        
        return actions


class Glint(Intention):
    """Gains 2 Strength."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Glint", enemy)
        self.base_strength_gain = 2
    
    def execute(self) -> List:
        """Execute glint - gain strength."""
        return [ApplyPowerAction(
            power=PowerType.STRENGTH,
            target=self.enemy,
            amount=self.base_strength_gain,
            duration=-1
        )]


class Taunt(Intention):
    """Applies 2 Weak and 2 Vulnerable."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Taunt", enemy)
        self.base_amount = 2
    
    def execute(self) -> List:
        """Execute taunt - apply debuffs."""
        from engine.game_state import game_state
        
        actions = []
        player = game_state.player
        
        # Apply Weak
        actions.append(ApplyPowerAction(
            power=PowerType.WEAK,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        # Apply Vulnerable
        actions.append(ApplyPowerAction(
            power=PowerType.VULNERABLE,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        return actions


class Anger(Intention):
    """Removes all buffs. Gains 4 Strength."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Anger", enemy)
        self.base_strength_gain = 4
    
    def execute(self) -> List:
        """Execute anger - remove buffs and gain strength."""
        from powers.base import Power
        
        actions = []
        
        # Remove all buffs (positive powers)
        # TODO: Implement RemoveBuffAction or clear positive powers
        # For now, just gain strength
        actions.append(ApplyPowerAction(
            power=PowerType.STRENGTH,
            target=self.enemy,
            amount=self.base_strength_gain,
            duration=-1
        ))
        
        return actions


class Escalate(Intention):
    """Deals 16×2 damage."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Escalate", enemy)
        self.base_damage = 16
        self._hits = 2
    
    def execute(self) -> List:
        """Execute escalate - double hit."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self._hits):
            damage = self.enemy.calculate_damage(self.base_damage)
            actions.append(AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        return actions
