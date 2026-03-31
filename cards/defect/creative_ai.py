"""Defect rare power card - Creative AI."""

from typing import List

from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from powers.definitions.creative_ai import CreativeAIPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class CreativeAI(Card):
    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    upgrade_cost = 2

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(CreativeAIPower(owner=game_state.player), game_state.player))
