"""Silent uncommon skill card - Tactician."""

from actions.combat import GainEnergyAction
from cards.base import COST_UNPLAYABLE, Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Tactician(Card):
    """Unplayable. When discarded, gain Energy."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = COST_UNPLAYABLE
    base_magic = {"energy": 1}

    upgrade_magic = {"energy": 2}

    def on_discard(self):
        from engine.runtime_api import add_actions

        add_actions([GainEnergyAction(energy=self.get_magic_value("energy"))])
