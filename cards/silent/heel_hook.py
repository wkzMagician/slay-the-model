"""Silent common attack card - Heel Hook."""

from typing import List

from actions.card import DrawCardsAction
from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class HeelHook(Card):
    """Deal damage. If target is Weak, gain energy and draw a card."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 5

    upgrade_damage = 8

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is None or target.get_power("Weak") is None:
            return
        from engine.runtime_api import add_actions

        add_actions([
            GainEnergyAction(energy=1),
            DrawCardsAction(count=1),
        ])
