"""
Ironclad Rare Attack card - Fiend Fire
"""

from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FiendFire(Card):
    """Exhaust all cards in hand, deal damage for each"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 2
    
    base_magic = {"exhaust_damage": 7}
    upgrade_magic = {"exhaust_damage": 10}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)
        
        player = game_state.player
        hand = player.card_manager.get_pile('hand')
        assert hand is not None

        # Count cards in hand before exhausting
        cards_to_exhaust = len(hand)

        # Exhaust all cards
        for i in range(cards_to_exhaust):
            actions.append(ExhaustCardAction(card=hand[i], source_pile="hand"))

        # Deal damage for each card exhausted
        damage = self._magic.get("exhaust_damage", 7)
        for _ in range(cards_to_exhaust):
            if target and target.hp > 0:
                actions.append(AttackAction(damage=damage, target=target, source=player))

        return actions
