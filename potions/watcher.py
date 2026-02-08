# Watcher Potions - Character-specific potions for Watcher
from typing import List
from actions.base import Action
from actions.card import AddCardAction
from potions.base import Potion
from utils.types import RarityType
from utils.random import get_random_card
from utils.registry import get_registered_instance, register

# Common Potions
@register("potion")
class BottledMiracle(Potion):
    """Add 2 Miracle cards to hand (4 with Sacred Bark) - Watcher only"""
    rarity = RarityType.COMMON
    category = "Watcher"
    name = "Bottled Miracle"

    def __init__(self):
        super().__init__()
        self._amount = 2  # Sacred Bark doubles to 4

    def on_use(self, target) -> List[Action]:
        from actions.card import AddCardAction
        from utils.random import get_random_card
        
        actions = []
        for _ in range(self.amount):
            # 不是random, 而是固定的miracle card
            miracle_card = get_registered_instance("card", "Miracle")
            if miracle_card:
                actions.append(AddCardAction(card=miracle_card, dest_pile='hand'))
        
        return actions

# Uncommon Potions
@register("potion")
class StancePotion(Potion):
    """Enter Calm or Wrath - Watcher only"""
    rarity = RarityType.UNCOMMON
    category = "Watcher"
    name = "Stance Potion"

    def __init__(self):
        super().__init__()

    def on_use(self, target) -> List[Action]:
        # Let player choose between Calm and Wrath
        # Note: This needs stance system implementation
        # TODO: Implement stance selection
        return []

# Rare Potions
@register("potion")
class Ambrosia(Potion):
    """Enter Divinity - Watcher only"""
    rarity = RarityType.RARE
    category = "Watcher"
    name = "Ambrosia"

    def __init__(self):
        super().__init__()

    def on_use(self, target) -> List[Action]:
        # Enter Divinity stance
        # Note: This needs stance system implementation
        # TODO: Implement Divinity stance entry
        return []