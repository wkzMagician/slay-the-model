"""
Colorless Rare Skill card - Violence
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

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
    base_magic = {"cards": 3}
    base_exhaust = True
    
    upgrade_magic = {"cards": 4}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        from engine.game_state import game_state
        from actions.card import MoveCardAction

        super().on_play(targets)

        actions = []
        # Draw 3/4 random Attacks from draw pile into hand
        draw_count = get_magic_value(self, "cards")

        if game_state.player and hasattr(game_state.player, "card_manager"):
            draw_cards = list(game_state.player.card_manager.get_pile("draw_pile"))
            attack_cards = [c for c in draw_cards if c.card_type == CardType.ATTACK]

            # Get up to draw_count random attacks
            selected = get_rng("shuffle").sample(attack_cards, min(draw_count, len(attack_cards)))

            for card in selected:
                actions.append(MoveCardAction(
                    card=card,
                    src_pile="draw_pile",
                    dst_pile="hand"
                ))

        from engine.game_state import game_state

        add_actions(actions)

        return
