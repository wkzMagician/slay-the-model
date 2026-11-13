"""
Colorless Uncommon Skill card - Madness
"""
from engine.random_streams import get_rng
from typing import List
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


def _turn_cost(card: Card) -> int:
    """Read costForTurn independently of energy and free-to-play-once state."""
    return card._cost if card.cost_until_end_of_turn is None else card.cost_until_end_of_turn


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
            better = any(_turn_cost(card) > 0 for card in hand_cards)
            if not better and not any(card._cost > 0 for card in hand_cards):
                return
            while True:
                card = get_rng("card_random").choice(hand_cards)
                cost = _turn_cost(card) if better else card._cost
                if cost > 0:
                    card._cost = 0
                    card.cost_until_end_of_turn = 0
                    if card.cost_until_played is not None:
                        card.cost_until_played = 0
                    return
