from actions.combat_status import ApplyPowerAction
from cards.base import Card
from engine.runtime_api import add_action
from powers.definitions.vulnerable import VulnerablePower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Indignation(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"vuln": 3}
    upgrade_magic = {"vuln": 5}
    text_name = "Indignation"
    text_description = "Apply {magic.vuln} Vulnerable."

    # todo: 效果不对。应为：若不在愤怒，则进入愤怒；若已在愤怒，对所有敌人施加易伤
    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))
