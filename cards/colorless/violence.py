"""
Colorless Rare Skill card - Violence
"""

from typing import List
from actions.base import Action
from actions.card import MoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.dynamic_values import get_magic_value
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Violence(Card):
    """Put random Attacks from draw pile into hand, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_magic = {"draw_attack": 3}
    base_exhaust = True
    
    upgrade_magic = {"draw_attack": 4}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state
        from actions.card import MoveCardAction

        actions = super().on_play(target)

        # Draw 3/4 random Attacks from draw pile into hand
        draw_count = get_magic_value(self, "draw_attack")

        if game_state.player and hasattr(game_state.player, "card_manager"):
            draw_cards = list(game_state.player.card_manager.get_pile("draw_pile"))
            attack_cards = [c for c in draw_cards if c.card_type == CardType.ATTACK]

            # Get up to draw_count random attacks
            import random
            selected = random.sample(attack_cards, min(draw_count, len(attack_cards)))

            for card in selected:
                actions.append(MoveCardAction(
                    card=card,
                    src_pile="draw_pile",
                    dst_pile="hand"
                ))

        return actions
