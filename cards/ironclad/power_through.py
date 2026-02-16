"""
Ironclad Uncommon Skill card - Power Through
"""

from typing import List
from actions.base import Action
from actions.card import AddCardAction
from actions.combat import GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class PowerThrough(Card):
    """Gain block, add a random card to hand"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 15

    upgrade_block = 20

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Add 2 Wound(Status Card) to hand
        from cards.colorless import Wound
        for _ in range(2):
            actions.append(AddCardAction(card=Wound(), dest_pile="hand"))
        return actions
