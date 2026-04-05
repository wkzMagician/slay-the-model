from actions.card import AddCardAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class DeceiveReality(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 7
    text_name = "Deceive Reality"
    text_description = "Gain {block} Block. Add a Safety into your hand."

    def on_play(self, targets: List = []):
        from cards.watcher.safety import Safety

        super().on_play(targets)
        add_action(AddCardAction(Safety(), dest_pile="hand"))
