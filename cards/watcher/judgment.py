from actions.combat_damage import LoseHPAction
from cards.base import Card
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Judgment(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"threshold": 30}
    upgrade_magic = {"threshold": 40}
    text_name = "Judgment"
    text_description = "If the enemy has {magic.threshold} HP or less, it dies."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is not None and target.hp <= self.get_magic_value("threshold"):
            add_action(LoseHPAction(amount=target.hp, target=target, source=self, card=self))
