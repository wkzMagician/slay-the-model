"""
Colorless Curse card - Decay
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.combat import DealDamageAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, DamageType, RarityType


@register("card")
class Decay(Card):
    """Unplayable, deal 2 damage at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    base_magic = {"turn_end_damage": 2}
    upgradeable = False

    def on_player_turn_end(self):
        """Deal damage at end of turn"""
        from engine.game_state import game_state

        super().on_player_turn_end()

        actions = []
        damage_amount = self.get_magic_value("turn_end_damage")
        actions.append(DealDamageAction(
            damage=damage_amount,
            target=game_state.player,
            damage_type=DamageType.MAGICAL
        ))

        from engine.game_state import game_state

        add_actions(actions)

        return
