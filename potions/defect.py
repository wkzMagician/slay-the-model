# Defect Potions - Character-specific potions for Defect
from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from potions.base import Potion
from utils.types import RarityType
from utils.registry import register

# Common Potions
@register("potion")
class FocusPotion(Potion):
    """Gain 2 Focus (4 with Sacred Bark) - Defect only"""
    rarity = RarityType.COMMON
    category = "Defect"
    name = "Focus Potion"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, target) -> List[Action]:
        return [ApplyPowerAction(power="Focus", target=target, amount=self.amount)]

# Rare Potions
@register("potion")
class EssenceOfDarkness(Potion):
    """Channel 1 Dark orb per Orb slot (2 per slot with Sacred Bark) - Rare"""
    rarity = RarityType.RARE
    category = "Defect"
    name = "Essence of Darkness"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2 (dark orbs per slot)

    def on_use(self, target) -> List[Action]:
        from engine.game_state import game_state
        # Channel Dark orbs for each orb slot
        # Note: This needs to use channel_orb action
        # TODO: Implement proper channel orb action
        return []

# Uncommon Potions
@register("potion")
class PotionOfCapacity(Potion):
    """Gain 2 Orb slots (4 with Sacred Bark) - Defect only"""
    rarity = RarityType.UNCOMMON
    category = "Defect"
    name = "Potion of Capacity"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, target) -> List[Action]:
        # Gain orb slots
        # Note: This needs orb slot modification action
        # TODO: Implement orb slot gain action
        return []