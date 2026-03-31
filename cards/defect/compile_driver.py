"""Defect common attack card - Compile Driver."""

from typing import List

from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class CompileDriver(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 1
    base_damage = 7
    upgrade_damage = 10

    @property
    def draw(self) -> int:
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None:
            return 0
        orb_types = {type(orb).__name__ for orb in player.orb_manager.orbs}
        return len(orb_types)

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.runtime_api import add_action

        if self.draw > 0:
            add_action(DrawCardsAction(count=self.draw))
