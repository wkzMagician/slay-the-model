"""Ironclad-specific relics - all Ironclad relics in one file."""
from typing import List
from actions.base import Action
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


# Common Relics
@register("relic")
class BurningBlood(Relic):
    """Start combat with Strength"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 1 Strength at start of combat"""
        from actions.combat import HealAction
        return [HealAction(target=player, amount=6)]