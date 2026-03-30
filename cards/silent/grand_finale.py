"""Silent rare attack card - Grand Finale."""

from typing import List

from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class GrandFinale(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_ALL

    base_cost = 0
    base_damage = 50

    upgrade_damage = 60

    def can_play(self, ignore_energy=False):
        playable, reason = super().can_play(ignore_energy)
        if not playable:
            return playable, reason
        from engine.game_state import game_state
        if len(game_state.player.card_manager.get_pile('draw_pile')) > 0:
            return False, 'Draw pile is not empty.'
        return True, None
