from actions.combat_damage import DealDamageAction
from engine.runtime_api import add_action
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class OmegaPower(Power):
    name = "Omega"
    description = "At the end of your turn, deal {amount} damage to ALL enemies."
    stack_type = StackType.MULTI_INSTANCE

    def on_turn_end(self):
        super().on_turn_end()
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        for enemy in list(game_state.current_combat.enemies if game_state.current_combat else []):
            if enemy.is_dead():
                continue
            add_action(DealDamageAction(self.amount, target=enemy, source=player))
