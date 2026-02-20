"""The Champ intentions - Act 2 Boss enemy."""

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention
from powers.base import PowerType

if TYPE_CHECKING:
    from enemies.act2.the_champ import TheChamp


class HeavySlash(Intention):
    """Deals 16 damage (18 on A4+)."""
    
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
    """Deals 12 damage (14 on A4+). Applies 2 Frail and 2 Vulnerable."""
    
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
    """Gains 15 Block and 5 Metallicize (varies by ascension)."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Defensive Stance", enemy)
        self.base_block = 15
        self.base_metallicize = 5
    
    def execute(self) -> List:
        """Execute defensive stance - gain block and metallicize."""
        from powers.definitions.metallicize import MetallicizePower
        
        actions = []
        
        # Gain block
        actions.append(GainBlockAction(
            block=self.base_block,
            target=self.enemy
        ))
        
        # Gain Metallicize
        actions.append(ApplyPowerAction(
            power=MetallicizePower,
            target=self.enemy,
            amount=self.base_metallicize,
            duration=-1
        ))
        
        return actions


class Gloat(Intention):
    """Gains 2 Strength (3 on A4+, 4 on A19+)."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Gloat", enemy)
        self.base_strength_gain = 2
    
    def execute(self) -> List:
        """Execute gloat - gain strength."""
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
    """Removes all Debuffs. Gains 6 Strength (9 on A4+, 12 on A19+)."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Anger", enemy)
        self.base_strength_gain = 6
    
    def execute(self) -> List:
        """Execute anger - remove debuffs and gain strength."""
        actions = []
        
        # Remove all debuffs (negative powers)
        # Clear all debuff powers from enemy
        if hasattr(self.enemy, 'powers') and self.enemy.powers:
            debuffs_to_remove = []
            for power in self.enemy.powers:
                if hasattr(power, 'is_buff') and not power.is_buff:
                    debuffs_to_remove.append(power)
            for debuff in debuffs_to_remove:
                self.enemy.powers.remove(debuff)
        
        # Gain strength
        actions.append(ApplyPowerAction(
            power=PowerType.STRENGTH,
            target=self.enemy,
            amount=self.base_strength_gain,
            duration=-1
        ))
        
        return actions


class Execute(Intention):
    """Deals 10×2 damage."""
    
    def __init__(self, enemy: "TheChamp"):
        super().__init__("Execute", enemy)
        self.base_damage = 10
        self._hits = 2
    
    def execute(self) -> List:
        """Execute - double hit."""
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