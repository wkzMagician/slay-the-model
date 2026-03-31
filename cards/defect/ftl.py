"""Defect uncommon attack card - FTL."""

from typing import List

from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FTL(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_damage = 5
    base_magic = {"limit": 3}
    upgrade_damage = 6
    upgrade_magic = {"limit": 4}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if game_state.current_combat is not None and game_state.current_combat.combat_state.turn_cards_played < self.get_magic_value("limit"):
            add_action(DrawCardsAction(count=1))
