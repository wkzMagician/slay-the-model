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

    @property
    def cost(self) -> int:
        from engine.game_state import game_state

        combat = getattr(game_state, 'current_combat', None)
        discarded = combat.combat_state.discarded_cards_this_turn if combat is not None else 0
        return max(0, self._cost - discarded)
