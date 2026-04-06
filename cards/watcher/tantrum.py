from actions.card_choice import MoveCardAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
from engine.runtime_api import add_actions
from typing import List
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType, StatusType, TargetType


@register("card")
class Tantrum(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 3
    upgrade_damage = 4
    base_attack_times = 3
    text_name = "Tantrum"
    text_description = "Deal {damage} damage {attack_times} times. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_actions(
            [
                ChangeStanceAction(StatusType.WRATH),
                MoveCardAction(self, "discard_pile", "draw_pile", position=PilePosType.RANDOM),
            ]
        )
