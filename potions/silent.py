# Silent Potions - Character-specific potions for Silent
from typing import List
from actions.base import Action
from actions.card import AddCardAction
from actions.combat import ApplyPowerAction
from potions.base import Potion
from utils.types import RarityType
from utils.random import get_random_card
from utils.registry import get_registered_instance, register

# Common Potions
@register("potion")
class PoisonPotion(Potion):
    """Apply 6 Poison to target enemy (12 with Sacred Bark) - Silent only"""
    rarity = RarityType.COMMON
    category = "Silent"
    name = "Poison Potion"

    def __init__(self):
        super().__init__()
        self._amount = 6  # Sacred Bark doubles to 12

    def on_use(self, target) -> List[Action]:
        return [ApplyPowerAction(power="Poison", target=target, amount=self.amount, duration=self.amount)]

# Uncommon Potions
@register("potion")
class CunningPotion(Potion):
    """Add 3 Shiv+ cards to hand (6 with Sacred Bark) - Silent only"""
    rarity = RarityType.UNCOMMON
    category = "Silent"
    name = "Cunning Potion"

    def __init__(self):
        super().__init__()
        self._amount = 3  # Sacred Bark doubles to 6

    def on_use(self, target) -> List[Action]:
        from actions.card import AddCardAction
        from utils.random import get_random_card
        
        actions = []
        for _ in range(self.amount):
            shiv_card = get_registered_instance("card", "Shiv")
            if shiv_card:
                shiv_card.upgrade()  # Upgrade to Shiv+
                actions.append(AddCardAction(card=shiv_card, dest_pile='hand'))
        
        return actions

# Rare Potions
@register("potion")
class GhostInAJar(Potion):
    """Gain 1 Intangible (2 with Sacred Bark) - Silent only"""
    rarity = RarityType.RARE
    category = "Silent"
    name = "Ghost in a Jar"

    def __init__(self):
        super().__init__()
        self._amount = 1  # Sacred Bark doubles to 2

    def on_use(self, target) -> List[Action]:
        from engine.game_state import game_state
        return [ApplyPowerAction(power="Intangible", target=game_state.player, amount=self.amount)]