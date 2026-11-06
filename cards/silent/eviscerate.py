"""Silent uncommon attack card - Eviscerate."""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Eviscerate(Card):
    """Costs less for each card discarded this turn."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 3
    base_damage = 7
    base_attack_times = 3

    upgrade_damage = 9

    def did_discard(self) -> None:
        """A discard reduces the current turn cost, not the combat base cost."""
        turn_cost = self.cost_until_end_of_turn
        if turn_cost is None:
            turn_cost = self._cost
        self.cost_until_end_of_turn = max(0, turn_cost - 1)

    def on_draw(self, card):
        if card is not self:
            return
        from engine.game_state import game_state
        combat = getattr(game_state, 'current_combat', None)
        discarded = combat.combat_state.discarded_cards_this_turn if combat is not None else 0
        self.cost_until_end_of_turn = max(0, self._cost - discarded)
