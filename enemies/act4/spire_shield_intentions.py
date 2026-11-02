"""Spire Shield Elite intentions for Act 4."""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from typing import List

from actions.base import Action
from actions.combat import ApplyPowerAction, AttackAction, GainBlockAction
from enemies.intention import Intention
from powers.definitions.focus import FocusPower
from powers.definitions.strength import StrengthPower


class Bash(Intention):
    """Deal damage and apply a conditional debuff."""

    def __init__(self, enemy):
        super().__init__("Bash", enemy)

    def execute(self):
        from engine.game_state import game_state

        player = game_state.player
        damage = get_rng("ai").choice([12, 14])
        actions = [
            AttackAction(
                damage=damage,
                target=player,
                source=self.enemy,
                damage_type="attack",
            )
        ]

        has_orb_slot = (
            hasattr(player, "orb_manager")
            and getattr(player.orb_manager, "max_orb_slots", 0) > 0
        )
        if has_orb_slot and get_rng("ai").choice([True, False]):
            actions.append(ApplyPowerAction(FocusPower(amount=-1, owner=player), player))
        else:
            actions.append(ApplyPowerAction(StrengthPower(amount=-1, owner=player), player))

        from engine.game_state import game_state

        add_actions(actions)

        return
class Fortify(Intention):
    """All enemies gain 30 Block."""

    def __init__(self, enemy):
        super().__init__("Fortify", enemy)
        self.base_block = 30

    def execute(self):
        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None) or getattr(
            game_state, "combat", None
        )
        if combat is None:
            from engine.game_state import game_state
            add_actions([GainBlockAction(block=self.base_block, target=self.enemy)])
            return
        actions = []
        for enemy in combat.enemies:
            if enemy.is_alive:
                actions.append(GainBlockAction(block=self.base_block, target=enemy))
        from engine.game_state import game_state
        add_actions(actions)
        return
class Smash(Intention):
    """Deal heavy damage and gain block."""

    def __init__(self, enemy):
        super().__init__("Smash", enemy)

    def execute(self):
        from engine.game_state import game_state

        base_damage, fixed_block = get_rng("ai").choice(
            [(34, None), (38, None), (38, 99)]
        )
        block_gain = fixed_block if fixed_block is not None else base_damage
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
            GainBlockAction(block=block_gain, target=self.enemy),
        ]
        )
        return
