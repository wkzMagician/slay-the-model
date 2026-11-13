"""Deal damage to a random enemy whenever the owner gains positive Block."""
from typing import Any

from actions.random_damage import DamageRandomEnemyAction
from engine.runtime_api import add_action
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class JuggernautPower(Power):
    """Whenever you gain Block, deal 5/7 damage to a random enemy."""

    name = "Juggernaut"
    description = "Whenever you gain Block, deal damage to a random enemy."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_gain_block(self, amount: int, source: Any = None, card: Any = None):
        from engine.game_state import game_state

        if amount > 0 and game_state.current_combat is not None:
            add_action(DamageRandomEnemyAction(damage=self.amount, source=self.owner))
