"""Colorless token attack card - Shiv."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Shiv(Card):
    """Deal damage and exhaust."""

    card_type = CardType.ATTACK
    rarity = RarityType.SPECIAL

    base_cost = 0
    base_damage = 4
    base_exhaust = True
    upgrade_damage = 6

    @property
    def damage(self):
        from engine.game_state import game_state

        damage = self._damage
        player = getattr(game_state, "player", None)
        if player is not None:
            accuracy = player.get_power("Accuracy")
            if accuracy is not None:
                damage += accuracy.amount
        return damage
