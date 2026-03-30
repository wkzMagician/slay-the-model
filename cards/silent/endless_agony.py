"""Silent common attack card - Endless Agony."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class EndlessAgony(Card):
    """When drawn, add a copy to your hand. Exhaust."""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON

    base_cost = 0
    base_damage = 4
    base_exhaust = True

    upgrade_damage = 6

    def on_draw(self):
        from actions.card_lifecycle import AddCardAction
        from engine.runtime_api import add_actions

        add_actions([AddCardAction(card=self.copy(), dest_pile="hand")])
