# Defect Potions - Character-specific potions for Defect
from typing import List
from actions.base import Action, LambdaAction
from actions.combat import ApplyPowerAction
from orbs.dark import DarkOrb
from player.player import Player
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
        return [LambdaAction(func=lambda: [game_state.player.orb_manager.add_orb(orb=DarkOrb()) \
            for _ in range(game_state.player.orb_manager.max_orb_slots)])]

# Uncommon Potions
@register("potion")
class PotionOfCapacity(Potion):
    """Gain 3 Orb slots (6 with Sacred Bark) - Defect only"""
    rarity = RarityType.UNCOMMON
    category = "Defect"
    name = "Potion of Capacity"

    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, target) -> List[Action]:
        # Gain orb slots
        assert isinstance(target, Player), "Potion of Capacity can only be used by the player"
        return [LambdaAction(func=lambda: setattr(target.orb_manager, "max_slots", target.orb_manager.max_orb_slots + self.amount))]