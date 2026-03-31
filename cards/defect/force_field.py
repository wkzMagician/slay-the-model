"""Defect uncommon skill card - Force Field."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class ForceField(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 4
    base_block = 12
    upgrade_block = 16

    @property
    def cost(self) -> int:
        from engine.game_state import game_state

        reduction = 0
        if game_state.current_combat is not None:
            reduction = game_state.current_combat.combat_state.power_cards_played
        if self.cost_until_end_of_turn is not None:
            return self.cost_until_end_of_turn
        if self.cost_until_played is not None:
            return self.cost_until_played
        return max(0, self._cost - reduction)
