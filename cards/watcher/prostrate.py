from actions.watcher import GainMantraAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Prostrate(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 4
    upgrade_block = 6
    base_exhaust = True
    text_name = "Prostrate"
    text_description = "Gain {block} Block. Gain 2 Mantra. Exhaust."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(2))
