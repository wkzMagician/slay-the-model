from actions.combat import EndTurnAction
from actions.watcher import SkipEnemyTurnAction
from cards.base import Card
from engine.runtime_api import add_actions
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Vault(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 3
    upgrade_cost = 2
    base_exhaust = True
    text_name = "Vault"
    text_description = "End your turn. Take another turn after this one."

    # todo: 功能有漏洞。跳过怪物回合的时候，下一个回合怪物的意图将保持和上回合一致。当前没有实现
    def on_play(self, targets: List = []):
        add_actions([SkipEnemyTurnAction(), EndTurnAction()])
