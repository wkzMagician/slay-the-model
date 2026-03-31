"""Defect common skill card - TURBO."""

from typing import List

from actions.card_lifecycle import AddCardAction
from actions.combat import GainEnergyAction
from cards.base import Card
from cards.colorless.void import Void
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType


@register("card")
class TURBO(Card):
    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_magic = {"energy": 2}
    upgrade_magic = {"energy": 3}

    def on_play(self, targets: List[Creature] = []):
        from engine.runtime_api import add_actions

        add_actions([
            GainEnergyAction(energy=self.get_magic_value("energy")),
            AddCardAction(card=Void(), dest_pile="discard_pile", position=PilePosType.TOP),
        ])
