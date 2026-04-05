from actions.watcher import GainMantraAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Pray(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 5
    text_name = "Pray"
    text_description = "Gain {block} Block. Gain 3 Mantra."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(3))
