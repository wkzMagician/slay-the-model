"""Silent uncommon skill card - Calculated Gamble."""

from typing import List

from actions.card import DiscardCardAction, DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class CalculatedGamble(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_exhaust = True
    upgrade_exhaust = False

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        hand = list(game_state.player.card_manager.get_pile("hand"))
        draw_count = len(hand)
        actions = [DiscardCardAction(card=card, source_pile="hand") for card in hand]
        if draw_count > 0:
            actions.append(DrawCardsAction(count=draw_count))
        add_actions(actions)
