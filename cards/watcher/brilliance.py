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

    # todo: 重载 damage property
    def on_play(self, targets: List = []):
        mantra = game_state_module.game_state.player.get_power("Mantra")
        if mantra is not None:
            self._damage += mantra.amount
        super().on_play(targets)
        self._damage = self.base_damage if self.upgrade_level == 0 else self.upgrade_damage
