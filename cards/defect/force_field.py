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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            self._cost = max(0, self._cost - game_state.current_combat.combat_state.power_cards_played)

    def on_card_play(self, card, targets):
        if card.card_type != CardType.POWER:
            return
        from engine.game_state import game_state
        if game_state.player.card_manager.get_card_location(self) not in ("hand", "draw_pile", "discard_pile"):
            return
        previous = self._cost
        self._cost = max(0, previous - 1)
        # updateCost preserves the difference between cost and costForTurn.
        if self.cost_until_end_of_turn is not None:
            self.cost_until_end_of_turn = max(0, self.cost_until_end_of_turn + self._cost - previous)
