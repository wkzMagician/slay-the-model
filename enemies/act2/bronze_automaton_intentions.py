"""Bronze Automaton intentions."""

from typing import List
from enemies.intention import Intention
from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction, AddEnemyAction
from enemies.act2.bronze_orb import BronzeOrb


class SummonOrb(Intention):
    """Summon 2 Bronze Orbs."""

    def __init__(self, enemy):
        super().__init__("Summon Orb", enemy)

    def execute(self) -> List:
        """Summon 2 Bronze Orb minions."""
        actions = []
        # Summon 2 Bronze Orbs
        for _ in range(2):
            orb = BronzeOrb()
            actions.append(AddEnemyAction(orb))
        return actions


class Hit(Intention):
    """Deal 12 damage."""

    def __init__(self, enemy):
        super().__init__("Hit", enemy)
        self.base_damage = 12

    def execute(self) -> List:
        """Deal damage to player."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage, game_state.player, self.enemy, "attack")]


class Repair(Intention):
    """Gain 3 Strength and 9 Block (4 Strength A17+)."""

    def __init__(self, enemy):
        super().__init__("Repair", enemy)
        self.base_block = 9
        self.base_strength_gain = 3

    def execute(self) -> List:
        """Gain strength and block."""
        actions = []
        # Gain Strength (4 on A17+, 3 otherwise)
        # For simplicity, using base value
        actions.append(ApplyPowerAction("strength", self.enemy, self.base_strength_gain))
        # Gain Block
        actions.append(GainBlockAction(self.base_block, self.enemy))
        return actions


class HyperBeam(Intention):
    """Deal 45 damage (54 A17+)."""

    def __init__(self, enemy):
        super().__init__("Hyper Beam", enemy)
        self.base_damage = 45

    def execute(self) -> List:
        """Deal heavy damage to player."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage, game_state.player, self.enemy, "attack")]


class Unsummon(Intention):
    """Does nothing (Bronze Orbs return)."""

    def __init__(self, enemy):
        super().__init__("Unsummon", enemy)

    def execute(self) -> List:
        """Do nothing."""
        return []
