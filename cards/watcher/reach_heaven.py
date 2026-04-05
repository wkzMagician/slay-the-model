from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class ReachHeaven(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 10
    upgrade_damage = 15
    text_name = "Reach Heaven"
    text_description = "Deal {damage} damage. Shuffle a Through Violence into your draw pile."

    def on_play(self, targets: List = []):
        from cards.watcher.through_violence import ThroughViolence

        super().on_play(targets)
        add_action(AddCardAction(ThroughViolence(), dest_pile="draw_pile"))
