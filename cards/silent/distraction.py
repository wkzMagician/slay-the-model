"""Silent uncommon skill card - Distraction."""

from typing import List

from actions.card import ChooseAddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Distraction(Card):
    """Choose a random skill that costs 0 this turn. Exhaust."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([
            ChooseAddRandomCardAction(namespace=game_state.player.namespace, card_type=CardType.SKILL, cost_until_end_of_turn=0)
        ])
