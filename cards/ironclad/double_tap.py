"""
Ironclad Rare Skill card - Double Tap
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DoubleTap(Card):
    """This turn, your next 1/2 Attack is played twice"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1

    base_magic = {"double_card_num": 1}
    upgrade_magic = {"double_card_num": 2}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply DoubleTapPower
        double_card_num = self.get_magic_value("double_card_num")
        actions.append(ApplyPowerAction(power="DoubleTapPower", target=game_state.player, amount=double_card_num, duration=1))

        return actions
