from actions.watcher import ScryAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class JustLucky(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 3
    upgrade_damage = 4
    base_block = 2
    upgrade_block = 3
    text_name = "Just Lucky"
    text_description = "Deal {damage} damage. Scry 1. Gain {block} Block."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(1))
