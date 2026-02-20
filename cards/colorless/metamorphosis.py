"""
Colorless Rare Skill card - Metamorphosis
"""

from typing import List
from actions.base import Action
from actions.card import AddRandomCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Metamorphosis(Card):
    """Shuffle random Attacks into draw pile, cost 0 this combat, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"card_count": 3}
    base_exhaust = True

    upgrade_magic = {"card_count": 5}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state
        
        actions = super().on_play(target)

        # Shuffle random Attacks into draw pile
        card_count = self.get_magic_value("card_count")

        for _ in range(card_count):
            actions.append(AddRandomCardAction(
                pile="draw_pile",
                card_type=CardType.ATTACK,
                namespace=game_state.player.namespace,
                permanent_cost=0
            ))
        return actions
