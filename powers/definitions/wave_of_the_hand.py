from actions.combat_status import ApplyPowerAction
from engine.runtime_api import add_action
from powers.base import Power
from powers.definitions.weak import WeakPower
from utils.registry import register

@register("power")
class WaveOfTheHandPower(Power):
    name = "Wave of the Hand"
    description = "Whenever you gain Block this turn, apply {amount} Weak to all enemies."

    def on_gain_block(self, amount: int, player=None, source=None, card=None):
        from engine.game_state import game_state

        if amount <= 0 or self.owner is None:
            return
        for enemy in list(game_state.current_combat.enemies if game_state.current_combat else []):
            if enemy.is_dead():
                continue
            add_action(ApplyPowerAction(WeakPower(amount=self.amount, duration=self.amount, owner=enemy), enemy))
