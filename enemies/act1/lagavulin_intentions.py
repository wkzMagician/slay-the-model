"""Lagavulin elite enemy intentions."""
from engine.runtime_api import add_actions

from typing import TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy


class SleepIntention(Intention):
    """Sleep — enemy does not act this turn."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("sleep", enemy)
    
    def execute(self) -> None:
        """Sleep: do nothing."""
class StunnedIntention(Intention):
    """Stunned — does nothing for one turn."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("stunned", enemy)
    
    def execute(self) -> None:
        """Stunned: do nothing."""
class AttackIntention(Intention):
    """Attack — deals damage (18 base, 20 on A18+)."""

    def __init__(self, enemy: 'Enemy', damage: int = 18):
        super().__init__("attack", enemy)
        self.base_damage = damage
    
    def execute(self) -> None:
        """Execute Attack: deals damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        add_actions(
            [
                AttackAction(
                    damage=self.base_damage,
                    target=game_state.player,
                    source=self.enemy,
                    damage_type="attack",
                )
            ]
        )


class SiphonSoulIntention(Intention):
    """Siphon Soul — player loses Strength and Dexterity (amount each, 2 each on A18+)."""

    def __init__(self, enemy: 'Enemy', amount: int = 1):
        super().__init__("siphon_soul", enemy)
        self.base_amount = amount

    def execute(self) -> None:
        """Apply -amount Strength and -amount Dexterity to the player."""
        from actions.combat import ApplyPowerAction
        from powers.definitions.dexterity import DexterityPower
        from powers.definitions.strength import StrengthPower
        from engine.game_state import game_state

        if not game_state or not game_state.player:
            return

        amt = self.base_amount
        add_actions(
            [
                ApplyPowerAction(
                    DexterityPower(amount=-amt, duration=-1, owner=game_state.player),
                    game_state.player,
                ),
                ApplyPowerAction(
                    StrengthPower(amount=-amt, duration=-1, owner=game_state.player),
                    game_state.player,
                ),
            ]
        )
