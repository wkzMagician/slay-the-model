"""
Anchor - Common relic
Blocks the first attack that deals more than 5 damage each combat.
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class Anchor(Relic):
    """Blocks first attack dealing more than 5 damage each combat"""

    def __init__(self):
        super().__init__()
        self.idstr = "Anchor"
        self.name_key = "relics.anchor.name"
        self.description_key = "relics.anchor.description"
        self.rarity = RarityType.COMMON

        # Track if anchor has been used this combat
        self.anchor_used_this_combat = False

    def on_combat_start(self):
        """Reset anchor state at start of each combat"""
        self.anchor_used_this_combat = False

    def on_attacked(self, damage_info):
        """
        Called when the owner is about to take damage.

        If this is the first attack dealing more than 5 damage,
        block it and mark anchor as used.
        """
        if self.anchor_used_this_combat:
            return

        if damage_info.get('amount', 0) > 5 and not damage_info.get('blocked', False):
            # Block this attack
            damage_info['blocked'] = True
            damage_info['amount'] = 0
            self.anchor_used_this_combat = True
