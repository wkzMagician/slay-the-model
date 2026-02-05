"""
Burning Blood - Boss relic
At the start of each combat, lose 1 HP and gain 2 Strength.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BurningBloodBoss(Relic):
    """Burning Blood - Boss relic, lose HP and gain Strength"""

    def __init__(self):
        super().__init__()
        self.idstr = "BurningBloodBoss"
        self.name_key = "relics.burning_blood_boss.name"
        self.description_key = "relics.burning_blood_boss.description"
        self.rarity = RarityType.BOSS

    def on_combat_start(self):
        """Lose 1 HP and gain 2 Strength at start of combat"""
        from actions.health import LoseHPAction

        # Create lose HP action
        return LoseHPAction(amount=1)

    def on_combat_end(self, result):
        """Draw 3 cards after combat if won"""
        if result == "WIN":
            from actions.card import DrawCardsAction

            # Create a draw cards action with 3 cards
            return DrawCardsAction(count=3)
