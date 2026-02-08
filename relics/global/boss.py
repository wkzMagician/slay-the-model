"""
Boss Global Relics
Global relics available at boss rarity.
"""
from typing import List
from actions.base import Action
from actions.card import DrawCardsAction
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class SneckoEye(Relic):
    """At the start of your turn, draw 2 additional cards. 
    Start each combat Icon Confused.png Confused."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_combat_start(self, player, entities) -> List[Action]:
        """Start each combat confused"""
        # TODO: Create ConfusedPower and apply it here
        # from actions.combat import ApplyPowerAction
        # from powers import ConfusedPower
        # return [ApplyPowerAction(target=player, power=ConfusedPower())]
        return []
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Draw 2 additional cards at start of turn"""
        return [DrawCardsAction(count=2)]
