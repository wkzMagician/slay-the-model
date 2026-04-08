"""
Ironclad Uncommon Skill card - Battle Trance
"""
from engine.runtime_api import add_action, add_actions

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

    base_cost = 0
    base_draw = 3

    upgrade_draw = 4

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state

        super().on_play(targets)

        actions = []
        # Apply "Cannot Draw" power for this turn (draw already handled by base class)
        from powers.definitions.no_draw import NoDrawPower
        actions.append(ApplyPowerAction(power=NoDrawPower(duration=1, owner=target), target=target, amount=1, duration=1))

        from engine.game_state import game_state

        add_actions(actions)

        return
