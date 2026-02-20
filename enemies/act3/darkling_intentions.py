"""Darkling enemy intentions for Slay the Model."""

import random
from typing import List

from actions.combat import AttackAction, ApplyPowerAction, GainBlockAction
from enemies.intention import Intention


class Harden(Intention):
    """Darkling Harden intention - gain block."""

    def __init__(self, enemy):
        super().__init__("Harden", enemy)
        self.base_block = 12
        self.strength_gain = 0  # A17+: gains 2 Strength

    def execute(self) -> List:
        """Execute Harden intention."""
        from engine.game_state import game_state
        actions = []
        actions.append(GainBlockAction(self.base_block, self.enemy))
        # A17+: gains 2 Strength
        if game_state.ascension >= 17:
            actions.append(ApplyPowerAction(
                "strength", self.enemy, 2, -1
            ))
        return actions


class Nip(Intention):
    """Darkling Nip intention - deals damage."""

    def __init__(self, enemy):
        super().__init__("Nip", enemy)
        self.base_damage = 9  # Random 7-11, A17+: 9-13
        self._roll_damage()

    def _roll_damage(self):
        """Roll damage at start of combat."""
        from engine.game_state import game_state
        if game_state.ascension >= 17:
            self.base_damage = random.randint(9, 13)
        else:
            self.base_damage = random.randint(7, 11)

    def execute(self) -> List:
        """Execute Nip intention."""
        from engine.game_state import game_state
        return [AttackAction(
            self.enemy.get_damage(self.base_damage),
            game_state.player,
            self.enemy,
            "attack"
        )]


class Chomp(Intention):
    """Darkling Chomp intention - deals 8x2 damage."""

    def __init__(self, enemy):
        super().__init__("Chomp", enemy)
        self.base_damage = 8
        self.hit_count = 2

    def execute(self) -> List:
        """Execute Chomp intention."""
        from engine.game_state import game_state
        actions = []
        for _ in range(self.hit_count):
            actions.append(AttackAction(
                self.enemy.get_damage(self.base_damage),
                game_state.player,
                self.enemy,
                "attack"
            ))
        return actions


class Regrowing(Intention):
    """Darkling Regrowing intention - does nothing."""

    def __init__(self, enemy):
        super().__init__("Regrowing...", enemy)

    def execute(self) -> List:
        """Execute Regrowing intention - do nothing."""
        return []


class Reincarnate(Intention):
    """Darkling Reincarnate intention - revive with 50% HP."""

    def __init__(self, enemy):
        super().__init__("Reincarnate", enemy)

    def execute(self) -> List:
        """Execute Reincarnate intention."""
        # Heal to 50% max HP
        heal_amount = self.enemy.max_hp // 2
        self.enemy.hp = heal_amount
        # Reset cannot be targeted state
        self.enemy._is_regrowing = False
        return []
