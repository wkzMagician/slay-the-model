"""Silent uncommon attack card - All Out Attack."""

import random
from typing import List

from actions.card import DiscardCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class AllOutAttack(Card):
    """Deal damage to all enemies and discard a random card."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 10

    upgrade_damage = 14

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        hand = list(game_state.player.card_manager.get_pile("hand"))
        if not hand:
            return
        add_actions([DiscardCardAction(card=random.choice(hand), source_pile="hand")])
