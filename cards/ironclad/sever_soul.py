"""
Ironclad Uncommon Attack card - Sever Soul
"""

from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SeverSoul(Card):
    """Exhaust non-Attack cards and deal damage"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 16

    upgrade_damage = 22

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        hand = game_state.player.card_manager.get_pile('hand')
        for card in hand:
            if card.card_type != CardType.ATTACK:
                actions.append(ExhaustCardAction(card=card, source_pile="hand"))

        return actions
