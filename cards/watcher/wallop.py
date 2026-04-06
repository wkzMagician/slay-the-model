from actions.combat import GainBlockAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Wallop(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 9
    upgrade_damage = 12
    text_name = "Wallop"
    text_description = "Deal {damage} damage. Gain Block equal to damage dealt."


    def on_damage_dealt(self, damage: int, target=None, card=None, damage_type: str = "direct"):
        if card is not self or damage <= 0:
            return
        add_action(GainBlockAction(damage, target=game_state_module.game_state.player))
