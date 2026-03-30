"""Silent uncommon skill card - Concentrate."""

from typing import List

from actions.card_choice import ChooseDiscardCardAction
from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Concentrate(Card):
    """Discard cards and gain energy."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"discard": 2, "energy": 2}

    upgrade_magic = {"discard": 1, "energy": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        add_actions([
            ChooseDiscardCardAction(pile="hand", amount=self.get_magic_value("discard")),
            GainEnergyAction(energy=self.get_magic_value("energy")),
        ])
