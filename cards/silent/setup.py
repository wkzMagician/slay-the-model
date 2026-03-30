"""Silent uncommon skill card - Setup."""

from typing import List

from actions.card import ChooseMoveAndSetCostAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Setup(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([ChooseMoveAndSetCostAction(src_pile='hand', dst_pile='draw_pile', amount=1)])
