"""
Ironclad Common Skill card - Armaments
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from actions.card import ChooseUpgradeCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Armaments(Card):
    """Gain block and upgrade a card in hand"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1
    base_block = 5
    base_magic = {"upgrade_hand": 1}

    upgrade_block = 7
    upgrade_magic = {"upgrade_hand": -1}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:        
        actions = super().on_play(targets)

        # Upgrade a card in hand
        upgrade_amount = self.get_magic_value("upgrade_hand")
        actions.append(ChooseUpgradeCardAction(pile="hand", amount=upgrade_amount))

        return actions
