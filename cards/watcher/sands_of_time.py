from cards.base import Card
import engine.game_state as game_state_module
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class SandsOfTime(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 4
    base_damage = 20
    upgrade_damage = 26
    base_retain = True
    text_name = "Sands of Time"
    text_description = "Retain. Deal {damage} damage. Retaining this card reduces its cost by 1."

    def on_player_turn_end(self):
        if self in game_state_module.game_state.player.card_manager.get_pile("hand") and self._cost > 0:
            self._cost -= 1
