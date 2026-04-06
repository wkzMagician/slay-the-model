from cards.base import Card
import engine.game_state as game_state_module
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Brilliance(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.RARE
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Brilliance"
    text_description = "Deal {damage} damage. Deals more damage for your Mantra."

    @property
    def damage(self) -> int:
        mantra = game_state_module.game_state.player.get_power("Mantra")
        return self._damage + (mantra.amount if mantra is not None else 0)
