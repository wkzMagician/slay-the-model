"""
Colorless Curse card - Pain
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.combat import LoseHPAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Pain(Card):
    """Unplayable, lose 1 HP when other cards are played"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    base_magic = {"damage_on_card_play": 1}
    upgradeable = False

    def on_card_play(self, card, player, targets):
        """Lose 1 HP when other cards are played"""
        # Only trigger when OTHER cards are played (not itself)
        if card is not self:
            damage_amount = self.get_magic_value("damage_on_card_play")
            from engine.game_state import game_state
            add_actions([LoseHPAction(amount=damage_amount)])
            return
        return