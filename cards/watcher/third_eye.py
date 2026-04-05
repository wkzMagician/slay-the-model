from actions.watcher import ScryAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class ThirdEye(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 7
    upgrade_block = 9
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 5}
    text_name = "Third Eye"
    text_description = "Gain {block} Block. Scry {magic.scry}."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(self.get_magic_value("scry")))
