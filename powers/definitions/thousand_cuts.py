"""A Thousand Cuts power for Silent."""

from actions.combat import DealDamageAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class ThousandCutsPower(Power):
    name = "A Thousand Cuts"
    description = "Whenever you play a card, deal damage to all enemies."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, targets):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        current_combat = getattr(game_state, "current_combat", None)
        enemies = getattr(current_combat, "enemies", []) if current_combat is not None else []
        player = game_state.player
        actions = [
            DealDamageAction(damage=self.amount, target=enemy, source=player, card=card)
            for enemy in enemies
            if getattr(enemy, "hp", 0) > 0
        ]
        if actions:
            add_actions(actions)
