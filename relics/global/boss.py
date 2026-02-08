"""
Boss Global Relics
Global relics available at boss rarity.
"""
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
        from actions.combat import ApplyPowerAction
        # todo: from powers.confused import ConfusedPower
        return [ApplyPowerAction(target=player, power=ConfusedPower())]