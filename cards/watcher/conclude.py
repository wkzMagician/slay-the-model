from actions.combat import EndTurnAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Conclude(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Conclude"
    text_description = "Deal {damage} damage to ALL enemies. End your turn."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(EndTurnAction())
