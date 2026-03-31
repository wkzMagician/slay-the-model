"""Defect rare attack card - All for One."""

from typing import List

from actions.card import MoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType


@register("card")
class AllForOne(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 2
    base_damage = 10
    upgrade_damage = 14

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        for card in list(game_state.player.card_manager.get_pile("discard_pile")):
            if card.cost == 0:
                add_action(MoveCardAction(card=card, src_pile="discard_pile", dst_pile="hand", position=PilePosType.TOP))
