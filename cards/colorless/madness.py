"""
Colorless Uncommon Skill card - Madness
"""
from engine.random_streams import get_rng
from typing import List
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Madness(Card):
    """Reduce cost of random card to 0 this combat, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_exhaust = True

    upgrade_cost = 0

    def on_play(self, targets: List[Creature] = []):
        from engine.game_state import game_state

        super().on_play(targets)

        if game_state.player and hasattr(game_state.player, "card_manager"):
            hand_cards = list(game_state.player.card_manager.get_pile("hand"))
            better_candidates = [card for card in hand_cards if card.cost > 0]
            fallback_candidates = [
                card for card in hand_cards
                if card.cost_until_end_of_turn is None and getattr(card, "_cost", None) not in (-1, -2) and card.cost > 0
            ]
            candidates = better_candidates or fallback_candidates
            if candidates:
                get_rng("card_random").choice(candidates).cost = 0
