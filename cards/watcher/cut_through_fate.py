from actions.card import DrawCardsAction
from actions.watcher import ScryAction
from cards.base import Card
from engine.runtime_api import add_actions
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class CutThroughFate(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 9
    base_magic = {"scry": 2}
    upgrade_magic = {"scry": 3}
    base_draw = 1
    text_name = "Cut Through Fate"
    text_description = "Deal {damage} damage. Scry {magic.scry}. Draw {draw} card."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_actions([ScryAction(self.get_magic_value("scry")), DrawCardsAction(self.draw)])
