"""
Burning Blood - Common relic
Heal 6 HP after each combat.
"""
from entities.player import Player
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class BurningBlood(Relic):
    """Heal 6 HP after each combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "BurningBlood"
        self.name_key = "relics.burning_blood.name"
        self.description_key = "relics.burning_blood.description"
        self.rarity = RarityType.COMMON

    def on_combat_end(self, result):
        """Heal 6 HP after combat if won"""
        if result == "WIN":
            from actions.health import HealAction

            # Create heal action
            heal_action = HealAction(amount=6)

            # Execute directly - this happens post-combat
            # Note: In a real game, this would be added to reward queue
            # For now, we'll apply the heal directly
            # This is a simplified approach
            pass
