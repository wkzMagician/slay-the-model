from engine.runtime_api import add_action
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
        """Deal damage to player at end of turn"""
        from engine.game_state import game_state
        super().on_player_turn_end()
        add_action(DealDamageAction(
            damage=get_magic_value(self, "burn_damage"),
            target=game_state.player,
            damage_type=DamageType.MAGICAL,
        ))
