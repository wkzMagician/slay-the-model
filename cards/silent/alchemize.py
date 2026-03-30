"""Silent rare skill card - Alchemize."""

from typing import List

from actions.reward import AddRandomPotionAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Alchemize(Card):
    """Obtain a random potion. Exhaust."""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_exhaust = True

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        add_actions([AddRandomPotionAction(character=game_state.player.namespace)])
