"""
Ironclad Uncommon Skill card - Sentinel
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction, ApplyPowerAction, GainEnergyAction
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

    base_magic = {"energy_on_exhaust": 2}
    upgrade_magic = {"energy_on_exhaust": 3}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Gain block
        actions.append(GainBlockAction(block=self.block, target=game_state.player))

        # Apply SentinelPower which gives energy on exhaust
        energy_on_exhaust = self.get_magic_value("energy_on_exhaust")
        actions.append(ApplyPowerAction(power="SentinelPower", target=game_state.player, amount=energy_on_exhaust, duration=1))

        return actions

    def on_exhaust(self) -> List[Action]:
        """Gain energy when this card is exhausted."""
        from actions.combat import GainEnergyAction
        energy_on_exhaust = self.get_magic_value("energy_on_exhaust")
        return [GainEnergyAction(energy=energy_on_exhaust)]
