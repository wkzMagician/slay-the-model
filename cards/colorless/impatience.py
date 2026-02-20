"""
Colorless Uncommon Skill card - Impatience
"""

from typing import List
from actions.base import Action
from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Impatience(Card):
    """Draw if no attacks in hand"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_draw = 0  # Conditional draw
    base_magic = {"draw_amount": 2}

    upgrade_magic = {"draw_amount": 3}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Check if there are any attacks in hand
        has_attack = False
        if game_state.player and hasattr(game_state.player, "card_manager"):
            hand_cards = game_state.player.card_manager.get_pile("hand")
            for card in hand_cards:
                if card.card_type == CardType.ATTACK:
                    has_attack = True
                    break

        # Only draw if no attacks in hand
        if not has_attack:
            draw_amount = self.get_magic_value("draw_amount")
            actions.append(DrawCardsAction(count=draw_amount))

        return actions
