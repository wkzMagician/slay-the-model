"""
Colorless Uncommon Skill card - Panic Button
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, GainBlockAction
from actions.card import ExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class PanicButton(Card):
    """Gain block, can't gain block for 2 turns, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_block = 30
    base_exhaust = True
    base_magic = {"turns": 2}

    upgrade_block = 40
    upgrade_magic = {"turns": 2}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain block
        actions.append(GainBlockAction(
            block=self.block,
            target=game_state.player,
            source=self
        ))

        # Apply "No Block" power for 2 turns
        no_block_duration = 2
        actions.append(ApplyPowerAction(
            power="NoBlock",
            target=game_state.player,
            duration=no_block_duration
        ))

        return actions
