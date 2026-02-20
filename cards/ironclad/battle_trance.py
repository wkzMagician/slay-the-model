"""
Ironclad Uncommon Skill card - Battle Trance
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction, ApplyPowerAction
from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BattleTrance(Card):
    """Draw 3/4 cards. Cannot draw cards this turn."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_draw = 3

    upgrade_draw = 4

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Apply "Cannot Draw" power for this turn (draw already handled by base class)
        from powers.definitions.battle_trance_draw_power import BattleTranceDrawPower
        actions.append(ApplyPowerAction(power="BattleTranceDrawPower", target=target, amount=1, duration=1))

        return actions
