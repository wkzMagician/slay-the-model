"""Silent uncommon skill card - Expertise."""

from typing import List

from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Expertise(Card):
    """Draw until you have six cards in hand."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1

    upgrade_cost = 0

    @property
    def draw(self) -> int:
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None:
            return 0
        return max(0, 6 - len(player.card_manager.get_pile("hand")))

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_actions

        if self.draw > 0:
            add_actions([DrawCardsAction(count=self.draw)])
