"""The Collector intentions - Act 2 Elite enemy."""

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention
from powers.base import PowerType

if TYPE_CHECKING:
    from enemies.act2.the_collector import TheCollector


class Spawn(Intention):
    """Summons up to 2 Torch Heads."""
    
    def __init__(self, enemy: "TheCollector"):
        super().__init__("Spawn", enemy)
    
    def execute(self) -> List:
        """Execute spawn - summon Torch Heads."""
        from engine.game_state import game_state
        from actions.combat import AddEnemyAction
        from enemies.act2.the_collector import TorchHead
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )
        
        actions = []
        
        # Count alive Torch Heads
        torch_head_count = sum(1 for e in enemies
                             if e.is_alive and isinstance(e, TorchHead))
        
        # Can only have max 2 Torch Heads
        to_summon = min(2, 2 - torch_head_count)
        
        for _ in range(to_summon):
            actions.append(AddEnemyAction(TorchHead))
        
        return actions


class Fireball(Intention):
    """Deals 18 damage."""
    
    def __init__(self, enemy: "TheCollector"):
        super().__init__("Fireball", enemy)
        self.base_damage = 18
    
    def execute(self) -> List:
        """Execute fireball attack."""
        from engine.game_state import game_state
        
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]


class Buff(Intention):
    """All enemies gain 3 Strength. Gains 15 Block."""
    
    def __init__(self, enemy: "TheCollector"):
        super().__init__("Buff", enemy)
        self.base_strength_gain = 3
        self.base_block = 15
    
    def execute(self) -> List:
        """Execute buff - strengthen all allies and gain block."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )
        
        actions = []
        
        # Apply strength to all enemies
        for enemy in enemies:
            if enemy.is_alive:
                actions.append(ApplyPowerAction(
                    power=PowerType.STRENGTH,
                    target=enemy,
                    amount=self.base_strength_gain,
                    duration=-1
                ))
        
        # Gain block for self
        actions.append(GainBlockAction(
            block=self.base_block,
            target=self.enemy
        ))
        
        return actions


class MegaDebuff(Intention):
    """Applies 3 Weak, 3 Vulnerable, and 3 Frail."""
    
    def __init__(self, enemy: "TheCollector"):
        super().__init__("Mega Debuff", enemy)
        self.base_amount = 3
    
    def execute(self) -> List:
        """Execute mega debuff - apply multiple debuffs."""
        from engine.game_state import game_state
        
        actions = []
        player = game_state.player
        
        # Apply 3 Weak
        actions.append(ApplyPowerAction(
            power=PowerType.WEAK,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        # Apply 3 Vulnerable
        actions.append(ApplyPowerAction(
            power=PowerType.VULNERABLE,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        # Apply 3 Frail
        actions.append(ApplyPowerAction(
            power=PowerType.FRAIL,
            target=player,
            amount=self.base_amount,
            duration=self.base_amount
        ))
        
        return actions


class Tackle(Intention):
    """Deals 7 damage (Torch Head attack)."""
    
    def __init__(self, enemy):
        super().__init__("Tackle", enemy)
        self.base_damage = 7
    
    def execute(self) -> List:
        """Execute tackle attack."""
        from engine.game_state import game_state
        
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(
            damage=damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]
