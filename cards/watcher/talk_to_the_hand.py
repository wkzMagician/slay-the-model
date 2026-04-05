from actions.combat_status import ApplyPowerAction
from cards.base import Card
from engine.runtime_api import add_action
from powers.definitions.talk_to_the_hand import TalkToTheHandPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class TalkToTheHand(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 5
    upgrade_damage = 8
    base_magic = {"block": 2}
    text_name = "Talk to the Hand"
    text_description = "Deal {damage} damage. Apply a debuff that gives you {magic.block} Block whenever you attack that enemy."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            add_action(ApplyPowerAction(TalkToTheHandPower(amount=self.get_magic_value("block"), owner=target), target))
