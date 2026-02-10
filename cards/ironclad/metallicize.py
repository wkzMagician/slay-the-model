"""
Ironclad Uncommon Power card - Metallicize
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Metallicize(Card):
    """Gain 3/4 block at end of your turn"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost =1
    base_magic = {"auto_block":3}
    upgrade_magic = {"auto_block":4}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply MetallicizePower
        auto_block = self.get_magic_value("auto_block")
        actions.append(ApplyPowerAction(power="MetallicizePower", target=game_state.player, amount=auto_block))

        return actions
