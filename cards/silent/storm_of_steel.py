"""Silent rare skill card - Storm of Steel."""

from typing import List

from actions.card import AddCardAction, DiscardCardAction
from cards.base import Card
from cards.colorless.shiv import Shiv
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class StormOfSteel(Card):
    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        hand = list(game_state.player.card_manager.get_pile('hand'))
        count = len(hand)
        actions = [DiscardCardAction(card=card, source_pile='hand') for card in hand]
        for _ in range(count):
            shiv = Shiv()
            if self.upgrade_level > 0:
                shiv.upgrade()
            actions.append(AddCardAction(card=shiv, dest_pile='hand'))
        add_actions(actions)
