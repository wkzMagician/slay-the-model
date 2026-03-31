"""Defect uncommon skill card - Aggregate."""

from typing import List

from actions.combat import GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Aggregate(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"per": 4}
    upgrade_magic = {"per": 3}

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        draw_count = len(game_state.player.card_manager.get_pile("draw_pile"))
        gain = draw_count // self.get_magic_value("per")
        add_action(GainEnergyAction(energy=gain))
