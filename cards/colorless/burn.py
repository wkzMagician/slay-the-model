from engine.runtime_api import add_action
from actions.base import LambdaAction
from cards.base import COST_UNPLAYABLE, Card
from actions.combat import DealDamageAction
from utils.dynamic_values import get_magic_value
from utils.types import CardType, DamageType


class Burn(Card):
    """Burn card - deals damage to owner at end of turn"""
    base_cost = COST_UNPLAYABLE
    card_type = CardType.STATUS
    
    base_magic = {"burn_damage": 2}
    upgrade_magic = {"burn_damage": 4}

    def on_player_turn_end(self):
        from actions.card_play_lifecycle import queue_turn_end_card
        queue_turn_end_card(self, LambdaAction(self._resolve_turn_end))

    def _resolve_turn_end(self):
        """Create damage only once the pending hand-card use starts."""
        from engine.game_state import game_state
        add_action(DealDamageAction(
            damage=get_magic_value(self, "burn_damage"),
            target=game_state.player,
            damage_type=DamageType.MAGICAL,
        ))
