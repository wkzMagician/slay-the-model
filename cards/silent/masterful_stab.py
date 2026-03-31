"""Silent uncommon attack card - Masterful Stab."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class MasterfulStab(Card):
    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_damage = 12

    upgrade_damage = 16

    def on_damage_taken(self, damage: int, source=None, player=None, entities=None):
        from engine.game_state import game_state

        if player is game_state.player and damage > 0:
            self._cost += 1

    def on_lose_hp(self, amount: int, source=None, card=None):
        if amount > 0:
            self._cost += 1
