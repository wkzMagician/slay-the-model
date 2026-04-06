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

    def on_play(self, targets: List = []):
        add_actions([SkipEnemyTurnAction(), EndTurnAction()])
