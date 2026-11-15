"""Defect rare skill card - Reboot."""
from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Reboot(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_draw = 4
    base_exhaust = True
    upgrade_draw = 6

    def on_play(self, targets: List[Creature] = []):
        from actions.card_shuffle import DrawAfterShuffleAction, queue_active_shuffle
        from engine.runtime_api import add_action

        queue_active_shuffle(include_hand=True)
        add_action(DrawAfterShuffleAction(count=self.draw))
