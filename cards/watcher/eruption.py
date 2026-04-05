from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class Eruption(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.STARTER
    base_cost = 2
    upgrade_cost = 1
    base_damage = 9
    upgrade_damage = 12
    text_name = "Eruption"
    text_description = "Deal {damage} damage. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))
