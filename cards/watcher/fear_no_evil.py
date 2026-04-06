from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType


@register("card")
class FearNoEvil(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 11
    text_name = "Fear No Evil"
    text_description = "Deal {damage} damage. If the enemy intends to attack, enter Calm."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None and getattr(target, "current_intention", None) is not None:
            if "attack" in getattr(target.current_intention, "name", "").lower():
                add_action(ChangeStanceAction(StatusType.CALM))
