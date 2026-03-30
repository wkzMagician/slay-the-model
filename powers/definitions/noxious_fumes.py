"""Silent power - Noxious Fumes."""

from actions.combat import ApplyPowerAction
from engine.runtime_api import add_actions
from powers.base import Power, StackType
from powers.definitions.poison import PoisonPower
from utils.registry import register


@register("power")
class NoxiousFumesPower(Power):
    name = "Noxious Fumes"
    description = "At the start of your turn, apply Poison to all enemies."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 2, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        from engine.game_state import game_state

        if game_state.current_combat is None:
            return

        add_actions([
            ApplyPowerAction(PoisonPower(amount=self.amount, duration=self.amount, owner=enemy), enemy)
            for enemy in game_state.current_combat.enemies
            if not enemy.is_dead()
        ])
        return
