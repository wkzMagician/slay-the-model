"""
Ironclad Uncommon Skill card - Sentinel
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction, GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Sentinel(Card):
    """Gain 5/8 block. On exhausted, gain 2/3 energy"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 5

    upgrade_block = 8

    base_magic = {"energy_on_exhaust": 2, "energy": 2}
    upgrade_magic = {"energy_on_exhaust": 3, "energy": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain block
        actions.append(GainBlockAction(block=self.block, target=game_state.player))

        return actions

    def on_exhaust(self) -> List[Action]:
        """Gain energy when this card is exhausted."""
        from actions.combat import GainEnergyAction
        energy_on_exhaust = self.get_magic_value("energy_on_exhaust")
        return [GainEnergyAction(energy=energy_on_exhaust)]
