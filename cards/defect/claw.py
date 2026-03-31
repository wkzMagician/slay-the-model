"""Defect common attack card - Claw."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Claw(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 3
    upgrade_damage = 5
    base_magic = {"bonus": 2}
    upgrade_magic = {"bonus": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state

        bonus = self.get_magic_value("bonus")
        for pile_name in ("hand", "draw_pile", "discard_pile", "exhaust_pile"):
            for card in game_state.player.card_manager.get_pile(pile_name):
                if isinstance(card, Claw):
                    card._damage += bonus
