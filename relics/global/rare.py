"""
Rare Global Relics
Global relics available to all characters at rare rarity.
"""
from typing import List
from actions.base import Action
from relics.base import Relic
from utils.types import CardType, RarityType
from utils.registry import register

@register("relic")
class BirdFacedUrn(Relic):
    """Whenever you play a Power card, heal 2 HP."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        
    def on_card_play(self, card, player, entities) -> List[Action]:
        if card.card_type == CardType.POWER:
            from actions.combat import HealAction
            return [HealAction(target=player, amount=2)]
        return []